# CodeDock Non-Goals

These boundaries prevent CodeDock from becoming an oversized or misleading project.

## 1. Not a general-purpose cloud IDE

CodeDock will not initially provide collaborative editing, persistent terminals, arbitrary package installation, long-running development servers, or unrestricted filesystem access.

## 2. Not an unrestricted code-hosting service

The first version will not provide public repositories, pull requests, issue tracking, or a complete Git hosting workflow. Submission source is retained only for the product features and retention policy that we explicitly define.

## 3. Not an AI coding assistant

AI code generation, code completion, natural-language problem solving, and AI-based grading are outside the core project. The project demonstrates execution infrastructure and security engineering.

## 4. Not a claim of perfect production isolation

The initial local implementation may use Docker with restrictive settings. This is useful for development and demonstration, but it is not automatically equivalent to a hardened multi-tenant production sandbox. The threat model and limitations must remain visible.

## 5. Not unlimited language coverage

A language is not considered supported merely because an image can start. Each language needs a runner, controlled commands, limits, result classification, cleanup behavior, and tests. Unsupported or disabled languages must be rejected by the API.

## 6. Not arbitrary SQL access

Submitted SQL will never run against CodeDock's application database. SQL execution uses a temporary database with an explicit dialect, schema, seed data, statement policy, timeout, and cleanup process.

## 7. Not a microservices showcase

The initial architecture will be a modular API plus separately running worker, database, and queue. Services will be split further only when a real operational or isolation boundary justifies it.

## 8. Not a performance benchmark suite

CodeDock will measure useful platform metrics and run bounded load tests, but it will not claim universal language benchmark results or guarantee identical timing across machines.

## 9. Not a replacement for professional security review

Automated security tests and documented controls improve the project, but they do not constitute a formal penetration test, compliance certification, or guarantee against unknown sandbox escapes.

## 10. Not a production deployment promise in the first milestone

Local reproducibility and a clear deployment design come before public hosting. Cloud deployment, managed databases, Kubernetes, and multi-region operation are later concerns rather than prerequisites for the core academic project.
