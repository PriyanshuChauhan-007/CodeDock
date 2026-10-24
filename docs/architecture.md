# CodeDock System Architecture

## 1. Architecture decision

CodeDock starts as a modular distributed application rather than a collection of microservices.

The first deployable units are:

1. **API service** — authentication, validation, persistence, query APIs, and job submission.
2. **Execution worker** — queue consumer, sandbox orchestration, execution, evaluation, and result persistence.
3. **PostgreSQL** — durable application state and execution history.
4. **Redis** — queue transport, short-lived coordination data, and rate-limit counters.
5. **Frontend** — browser client for authentication, submission, status, and results.

This boundary is deliberate. The API and worker have different trust and resource profiles, so they are separate processes. Splitting the API into many network services would add operational complexity before the system needs it.

```text
                         HTTPS
  ┌───────────────────────────────────────────────┐
  │                  React frontend                │
  │ editor • test cases • status • history         │
  └───────────────────────┬───────────────────────┘
                          │
                          ▼
  ┌───────────────────────────────────────────────┐
  │                  FastAPI API                   │
  │ auth • validation • authorization • HTTP API   │
  │ submission persistence • enqueue • read models │
  └───────────────┬───────────────────┬───────────┘
                  │                   │
                  │ SQL               │ queue job ID
                  ▼                   ▼
       ┌──────────────────┐  ┌──────────────────┐
       │    PostgreSQL    │  │      Redis       │
       │ durable state    │  │ queue + limits   │
       └────────┬─────────┘  └────────┬─────────┘
                │                     │
                │ result/status SQL   │ consume
                │                     ▼
                │           ┌──────────────────┐
                └───────────│ Execution worker │
                            │ claim • run •     │
                            │ evaluate • clean  │
                            └────────┬─────────┘
                                     │ controlled runtime boundary
                                     ▼
                            ┌──────────────────┐
                            │ Sandbox adapter  │
                            │ Docker/container │
                            │ or SQL/browser   │
                            └──────────────────┘
```

## 2. Component responsibilities

### 2.1 Frontend

The frontend is a client, not a trusted execution component. It:

- authenticates through the API;
- retrieves the enabled language registry;
- submits source and test cases;
- polls submission status in the first version;
- displays public result data while protecting hidden tests;
- provides submission history and filtering.

The frontend never decides whether a language is allowed, whether a user owns a submission, or what resource limits apply.

### 2.2 API service

The API is responsible for:

- request authentication and authorization;
- schema and size validation;
- language and policy validation;
- creating durable submission records;
- creating test-case records;
- enqueueing a small job message after the database transaction succeeds;
- returning status and result read models;
- applying rate limits;
- emitting request and audit logs.

The API does **not**:

- execute user source code;
- construct shell commands from request data;
- connect submitted SQL to the application database;
- trust status values supplied by a client;
- wait synchronously for a worker to finish.

### 2.3 PostgreSQL

PostgreSQL is the source of truth for durable state:

- users and sessions;
- language runtime configurations;
- submissions;
- test cases;
- execution attempts;
- per-test results;
- audit events.

The database stores lifecycle timestamps so queue wait, execution, evaluation, and total duration can be measured.

### 2.4 Redis

Redis is used for short-lived or transport concerns:

- queued job delivery;
- login and submission rate-limit counters;
- optional worker heartbeats;
- short-lived coordination locks.

Redis is not the durable source of truth for a submission result. A Redis outage must not make already persisted results disappear.

### 2.5 Execution worker

The worker:

1. receives a submission identifier;
2. loads the submission and test cases from PostgreSQL;
3. atomically claims an execution attempt;
4. validates that the language is still enabled;
5. creates an isolated workspace;
6. selects a registered language runner;
7. compiles and/or executes inside the appropriate sandbox;
8. captures bounded stdout, stderr, exit status, and resource data;
9. evaluates test cases;
10. persists the result and final status;
11. removes temporary resources even after failure.

The worker is the only component allowed to request sandbox execution. It still never passes arbitrary user-provided commands to a shell.

### 2.6 Sandbox adapters

The runner layer hides language-specific behavior behind a common contract.

```text
Language registry
      ↓
Runner selection
      ↓
prepare → compile (optional) → execute → classify → cleanup
```

Planned adapter categories:

- runtime runner: Python, JavaScript;
- compile-and-run runner: C, C++, C#, Java, TypeScript;
- database runner: SQL against a temporary database;
- browser validation runner: HTML/CSS in a restricted browser context.

The API knows language metadata, but the worker owns execution details.

## 3. Trust boundaries

```text
Untrusted browser input
        │ validation boundary
        ▼
API process
        │ persistence/queue boundary
        ▼
Worker process
        │ sandbox boundary
        ▼
Untrusted source execution
```

### Boundary A: browser to API

Requests are untrusted. Authentication, authorization, schema validation, request-size limits, and rate limiting happen here.

### Boundary B: API to queue

The queue message contains an opaque submission identifier and execution metadata, not an instruction string. The worker reloads authoritative data from PostgreSQL.

### Boundary C: worker to sandbox

Source code is treated as hostile. The sandbox receives only the required temporary workspace and explicit limits. It has no application credentials, no Docker socket, and no network access in the baseline design.

### Boundary D: sandbox to result store

Output is untrusted and bounded before persistence or display. Logs and API responses must avoid turning compiler output into an injection path.

## 4. Submission lifecycle

```text
                    API transaction
  client ────────► create submission ────────► QUEUED
                                                  │
                                                  │ worker claims
                                                  ▼
                                               RUNNING
                                                  │
                         ┌────────────────────────┼───────────────────────┐
                         │                        │                       │
                   compile fails            run fails              run succeeds
                         │                        │                       │
                         ▼                        ▼                       ▼
                COMPILATION_ERROR          RUNTIME_ERROR              EVALUATING
                                                                            │
                                         ┌──────────────────────────────────┼──────────────┐
                                         │                                  │              │
                                      all pass                          mismatch       limit/error
                                         │                                  │              │
                                         ▼                                  ▼              ▼
                                      PASSED                              FAILED       final failure
```

Other legal exits include `CANCELLED` before execution, and `SYSTEM_ERROR` when the platform cannot safely complete the attempt.

The state machine is persisted and checked in application code. A final state cannot be moved back to a non-final state.

## 5. Worker lifecycle

```text
IDLE
  │ receive job
  ▼
CLAIMING
  │ lock/attempt validation
  ▼
PREPARING
  │ workspace + runner setup
  ▼
COMPILING (when required)
  │
  ├── compilation error ──► FINALIZE
  │
  ▼
EXECUTING
  │
  ├── timeout/memory/output/runtime failure ──► FINALIZE
  │
  ▼
EVALUATING
  │ compare test results
  ▼
FINALIZE
  │ persist result, emit metrics, cleanup
  ▼
IDLE
```

Cleanup is attached to the finalization path and must run for successful, failed, timed-out, and interrupted executions.

## 6. Queue and consistency strategy

The API follows this order:

1. validate the request;
2. create the submission and test cases in one database transaction;
3. commit the transaction;
4. enqueue the submission identifier;
5. return the submission response.

This prevents a worker from receiving a job for data that was never committed.

The remaining commit-to-enqueue gap is handled with an outbox-style improvement when the queue implementation is introduced. The outbox record is committed with the submission and a dispatcher retries delivery until Redis accepts it.

Workers use an execution-attempt record and an idempotency check. If the same job is delivered twice, only one active attempt can own the submission. A duplicate delivery either observes the existing attempt or exits without overwriting a newer result.

## 7. Failure handling

### User-caused execution failures

These are final, explainable states:

- compilation error;
- runtime error;
- timeout;
- memory limit;
- output limit;
- security violation;
- failed test evaluation.

### Platform failures

These are not presented as a wrong answer:

- database unavailable;
- queue unavailable;
- worker crash;
- sandbox startup failure;
- result persistence failure;
- malformed internal runtime configuration.

Platform failures become `SYSTEM_ERROR` only after bounded retry behavior is exhausted. The worker records enough metadata for operators to investigate without exposing internal secrets to the user.

## 8. Data flow by execution category

### Runtime and compiled languages

```text
source + test cases
        ↓
temporary workspace
        ↓
restricted language container
        ↓
compile, if needed
        ↓
execute once per controlled evaluation plan
        ↓
bounded output and metrics
        ↓
test evaluator
```

The exact decision to run one process per test or one process with multiple inputs is a policy choice. The first implementation should favor isolation and simple cleanup, even if it is less optimized.

### SQL

```text
SQL + schema + seed data
        ↓
temporary database/container
        ↓
statement policy validation
        ↓
query timeout and row limit
        ↓
deterministic result comparison
        ↓
destroy temporary database
```

The application database is never part of this flow.

### HTML/CSS

```text
document + stylesheet + assertions
        ↓
restricted browser context
        ↓
network blocked and resource limits applied
        ↓
DOM/style/accessibility assertions
        ↓
browser cleanup
```

This is a later execution subsystem and will not block the first language runner milestones.

## 9. Observability design

Every request and execution should be traceable using:

- `request_id` for an API request;
- `submission_id` for the user-visible workflow;
- `execution_id` for one worker attempt;
- `worker_id` for the processing instance.

Important metrics:

- request latency;
- queue depth;
- queue wait duration;
- execution duration;
- evaluation duration;
- pass/fail rate by language;
- timeout and resource-limit counts;
- worker failure and retry counts;
- sandbox cleanup failures.

Logs must be structured and must not include passwords, tokens, database credentials, or unbounded source/output payloads.

## 10. Scaling path

The initial system can run one API process and one worker. The architecture supports later growth:

1. run multiple API processes behind a reverse proxy;
2. run multiple workers with a shared queue;
3. assign worker pools by execution category or language;
4. add an outbox dispatcher for reliable enqueueing;
5. move large source/results to object storage while keeping metadata in PostgreSQL;
6. introduce stronger sandbox isolation such as gVisor, Kata Containers, or Firecracker for a hostile multi-tenant deployment.

These are evolution points, not required components for the first local milestone.

## 11. Architecture decisions to verify in implementation

The following are decisions, not assumptions that can remain untested:

- Docker/container restrictions actually enforce the configured limits;
- worker cleanup runs on timeout and process interruption;
- duplicate queue delivery cannot overwrite a final result;
- hidden test data is excluded from user-facing responses;
- SQL execution cannot reach the application database;
- network access is disabled in every code runner;
- logs remain bounded and redacted;
- readiness checks detect dependency outages;
- state transitions reject illegal moves.

Each item must eventually have an automated test or an explicit operational verification procedure.
