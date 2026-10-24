# CodeDock Product Scope

## 1. Product statement

CodeDock is a secure, asynchronous, multi-language code execution and evaluation platform. It accepts source code and controlled test data, places execution work on a queue, runs the work inside a restricted language-specific sandbox, evaluates the result, and exposes an auditable execution history.

CodeDock is intended to demonstrate the engineering problems behind online judges and developer platforms:

- processing untrusted input safely;
- coordinating API requests, queues, workers, and persistent state;
- enforcing execution and resource limits;
- producing useful, explainable results;
- recovering from failed or duplicated work;
- measuring the system instead of treating execution as a black box.

The project is a portfolio-quality engineering system, not a collection of unrelated CRUD screens and not an AI-generated code-writing product.

## 2. Primary user flow

1. A user creates an account and signs in.
2. The user chooses an enabled language and provides source code.
3. The user supplies one or more test cases, subject to size and policy limits.
4. The API validates the request, stores the submission, and returns a submission ID.
5. A queue receives a small job message containing the submission identity.
6. A worker claims the job and records the execution lifecycle.
7. A language runner builds and/or executes the source inside a restricted sandbox.
8. The evaluator compares the produced result with the test cases.
9. The result and resource measurements are persisted.
10. The user observes the final status through the API and frontend.

The API must not wait for arbitrary source code to finish executing.

## 3. Initial product boundary

### Included

- user registration and login;
- authenticated submission ownership;
- asynchronous submissions;
- custom public and hidden test cases;
- submission history;
- explicit execution status transitions;
- compiler, runtime, timeout, memory, output, and evaluation errors;
- resource measurements where the runtime can provide them;
- language-specific sandbox runners;
- structured logs, health checks, and operational metrics;
- unit, integration, and security tests;
- OpenAPI documentation plus project-level architecture and security documentation.

### Initial language plan

The runtime registry will eventually cover:

- Python;
- C;
- C++;
- C#;
- Java;
- JavaScript;
- TypeScript;
- SQL with an explicitly documented database dialect;
- HTML and CSS through validation/rendering workflows rather than ordinary process execution.

Implementation will begin with Python, C++, JavaScript, and one SQL dialect. Additional languages will use the same runner contract instead of adding special cases throughout the API.

## 4. Execution categories

CodeDock will not pretend every supported language has the same execution model.

### Runtime languages

Python and JavaScript execute through a controlled interpreter/runtime.

### Compiled languages

C, C++, C#, Java, and TypeScript have a build stage followed by an execution stage. Compilation errors and runtime errors are separate result types.

### Database language

SQL runs against a temporary, isolated database populated with a declared schema and seed data. It must never run against CodeDock's own application database. The selected dialect and allowed statement policy are part of the product contract.

### Markup and stylesheet languages

HTML and CSS are validated or rendered in a browser-oriented sandbox. They are not passed to a host shell as if they were ordinary programs.

## 5. Submission lifecycle

The first version uses these statuses:

```text
QUEUED
RUNNING
EVALUATING
PASSED
FAILED
COMPILATION_ERROR
RUNTIME_ERROR
TIME_LIMIT_EXCEEDED
MEMORY_LIMIT_EXCEEDED
OUTPUT_LIMIT_EXCEEDED
SECURITY_VIOLATION
CANCELLED
SYSTEM_ERROR
```

Only documented state transitions are allowed. A completed submission cannot silently return to a running state.

## 6. Product principles

### Security before convenience

Untrusted source code is never executed directly on the API host. Sandboxing, limits, cleanup, and security tests are core product behavior.

### Asynchronous by design

The API records work and returns quickly. Workers perform execution independently and update durable state.

### Explainable results

Users should see why a submission failed: compilation output, runtime error, failed test information, timeout, memory limit, or output limit, subject to hidden-test protection.

### Explicit limitations

The project will document the security boundary of its local Docker-based implementation and will not claim that ordinary containers alone provide perfect hostile multi-tenant isolation.

### Reproducible development

The project should run through documented commands and Docker Compose without relying on a developer's machine-specific global state.

### Measurable behavior

Queue wait time, execution time, test outcomes, worker failures, and resource usage should be captured where possible.

## 7. Success criteria

The product is successful when a reviewer can:

1. register and authenticate;
2. submit code without blocking the API request;
3. observe queued and running states;
4. receive a deterministic result for multiple test cases;
5. see compilation and runtime failures separately;
6. verify that malicious or resource-intensive code is stopped;
7. inspect logs and execution metadata for a submission;
8. read the security limitations and reproduce the local setup;
9. understand the architecture from the repository documentation;
10. run the automated tests and see meaningful failure coverage.

## 8. Portfolio positioning

CodeDock should be presented as a compact execution platform and reliability/security case study. The strongest demonstration is not the number of languages; it is the combination of:

- a stateful asynchronous workflow;
- isolated execution;
- failure classification;
- ownership and authorization;
- resource enforcement;
- observability;
- tests for hostile inputs;
- transparent design trade-offs.
