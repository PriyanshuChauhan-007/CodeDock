# CodeDock

CodeDock is a secure, asynchronous, multi-language code execution and evaluation platform. It is designed as a portfolio-quality systems project demonstrating API design, queue-backed workers, sandboxed execution, resource limits, result evaluation, observability, and security testing.

## Current status

The project is currently in the foundation phase.

Completed:

- product scope and non-goals;
- system architecture;
- repository foundation.

Not implemented yet:

- authentication;
- submission APIs;
- worker execution;
- sandbox containers;
- frontend screens.

This is intentional. CodeDock is being built in small, tested stages rather than generated as one unverified application.

## Documentation

- [Product scope](docs/product-scope.md)
- [Non-goals](docs/non-goals.md)
- [System architecture](docs/architecture.md)

## Planned stack

- Python and FastAPI for the API;
- PostgreSQL for durable state;
- Redis for queue transport and rate limiting;
- Docker-based isolated execution for local development;
- React for the frontend;
- Pytest for automated tests.

## Local prerequisites

The complete local stack will require:

- Python 3.12 or newer;
- Docker Engine or Docker Desktop with Compose;
- Node.js and npm for the frontend milestone;
- Git.

Docker is not currently available in the development environment, so Docker-backed verification will be enabled in a later session when the runtime is available.

## Development principles

1. Never execute submitted source code directly on the API host.
2. Keep the API and execution worker as separate processes.
3. Treat Docker as a sandbox boundary with documented limitations, not as a claim of perfect isolation.
4. Add tests for both successful behavior and hostile inputs.
5. Keep database migrations, logs, and operational behavior reproducible.

## Repository workflow

Each implementation session should make one bounded change, run the narrowest meaningful checks, and leave the project in a readable state.
