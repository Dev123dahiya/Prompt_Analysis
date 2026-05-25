# Prompt Analysis Benchmark

![Language](https://img.shields.io/badge/language-Python-blue)
![Benchmark](https://img.shields.io/badge/type-LLM%20coding%20benchmark-green)
![Domain](https://img.shields.io/badge/domain-Leave%20Management-orange)
![Status](https://img.shields.io/badge/status-complete-brightgreen)

## Project Overview

This repository contains a complete benchmark package for evaluating LLM responses to a realistic, domain-specific full-stack coding task.

The benchmark is centered on a **Leave Management System** for a mid-sized organization. It tests whether an LLM can interpret detailed product requirements, implement business rules, apply security best practices, document setup and deployment, and produce maintainable production-style code.

## Links

| Resource | URL |
| --- | --- |
| GitHub Repository | `https://github.com/Dev123dahiya/Prompt_Analysis` |
| Live Deployment | `https://leave-request-management-system.vercel.app/` |

## Repository Contents

| Path | Description |
| --- | --- |
| `prompt.md` | Original MERN-stack coding prompt used for evaluation. |
| `justification.md` | Structured comparison framework and final verdict for Response A vs Response B. |
| `golden_response.py` | Root-level launcher required by the submission checklist. |
| `golden_response/` | Modular executable reference implementation for the core backend/domain behavior. |
| `golden_response/goldenresponse.md` | Written golden-output explanation for the prompt response. |
| `README.md` | Project overview, run instructions, and evaluation notes. |

## Repository Structure

```text
Prompt_Analysis/
|-- README.md
|-- prompt.md
|-- justification.md
|-- golden_response.py
`-- golden_response/
    |-- README.md
    |-- goldenresponse.md
    |-- __init__.py
    |-- __main__.py
    |-- cli.py
    |-- config.py
    |-- errors.py
    |-- models.py
    |-- security.py
    |-- server.py
    |-- service.py
    |-- tests.py
    `-- validators.py
```

## Benchmark Task

The prompt asks an LLM to build a MERN-stack Leave Management System with:

- Employee, Manager, and Admin role flows.
- Secure JWT authentication using httpOnly cookies.
- Role-based dashboards and permissions.
- Leave request creation, editing, cancellation, approval, and rejection.
- Weekday-only leave calculation.
- Leave balance enforcement.
- Pending request overlap prevention.
- Department-scoped manager access.
- Admin policy management and user management.
- CSV report generation.
- Responsive and accessible frontend requirements.
- Deployment guidance for Vercel, Render, and MongoDB Atlas.

## Golden Response

The `golden_response/` folder contains a structured Python reference implementation. It is designed for benchmark portability and focuses on the core backend rules from the prompt.

It includes:

- Signed-token authentication.
- Password hashing.
- Login and logout rate limiting.
- Structured API-style errors.
- Input sanitization and email validation.
- Weekday-only leave day calculation.
- Leave policy and balance checks.
- Pending leave overlap detection.
- Manager department authorization.
- Admin override handling.
- Pending request rejection on user deactivation.
- CSV report generation.
- A small standard-library HTTP API.
- Built-in self-test coverage for important edge cases.

> Note: The production prompt asks for a MERN implementation. The Python golden response is a portable reference solution for the benchmark's business logic, not a replacement for a full MERN deployment.

## Instructions for Running/Testing the Code

The golden response uses only the Python standard library.

Run the built-in self-test:

```bash
python -m golden_response --self-test
```

The root launcher also supports the required file name:

```bash
python golden_response.py --self-test
```

Expected output:

```text
Self-test passed.
```

Start the local reference API:

```bash
python -m golden_response --serve --port 8000
```

API base URL:

```text
http://127.0.0.1:8000
```

## Seeded Test Credentials

| Role | Email | Password |
| --- | --- | --- |
| Employee | `employee@example.com` | `Password123!` |
| Manager | `manager@example.com` | `Password123!` |
| Admin | `admin@example.com` | `Password123!` |

## Evaluation Methodology

Responses should be evaluated on implementation quality, requirement coverage, correctness, maintainability, and the quality of the accompanying justification. The goal is not only to check whether a response mentions the requested features, but whether it provides a solution that could realistically be built, tested, reviewed, and deployed.

### Scoring Rubric

| Category | Weight | What to Evaluate |
| --- | ---: | --- |
| Requirement coverage | 20% | Checks whether all explicit prompt requirements are addressed, including role dashboards, REST endpoints, leave policies, CSV reports, validation, documentation, and deployment notes. |
| Functional correctness | 20% | Verifies the actual business rules: weekday-only day calculation, balance enforcement, pending overlap prevention, manager department restriction, admin override behavior, and user deactivation handling. |
| Backend quality | 15% | Reviews API design, Express route structure, Mongoose models, indexes, middleware, pagination, filtering, structured JSON errors, and separation of concerns. |
| Security and validation | 15% | Checks password hashing, JWT httpOnly cookies, safe cookie options, CORS restrictions, Helmet, rate limiting, input sanitization, email validation, and prevention of sensitive data leakage. |
| Frontend quality | 10% | Evaluates role-based dashboards, responsive layout, modal behavior, accessible controls, ARIA labels, keyboard navigation, route lazy loading, and debounced search. |
| Documentation and deployment readiness | 10% | Checks README clarity, local setup steps, environment variable tables, seed instructions, test credentials, Vercel/Render/MongoDB Atlas deployment guidance, and known limitations. |
| Maintainability and code organization | 10% | Evaluates readability, modularity, naming, comments, error handling, edge-case coverage, and whether the implementation can be extended safely. |

### Suggested Rating Scale

| Score | Meaning |
| --- | --- |
| 1 | Fails the task; mostly irrelevant or non-functional. |
| 2 | Mentions some requirements but lacks usable implementation. |
| 3 | Partial implementation with major missing workflows or unsafe assumptions. |
| 4 | Usable foundation, but important constraints or edge cases are missing. |
| 5 | Good response that satisfies most requirements with moderate gaps. |
| 6 | Strong response with executable, well-structured implementation and only minor gaps. |
| 7 | Excellent production-quality response that fully satisfies explicit and implicit requirements. |

### Evaluation Workflow

1. Read `prompt.md` and list all explicit constraints.
2. Check whether the response provides runnable code, not only an architecture description.
3. Validate role-specific behavior for Employee, Manager, and Admin users.
4. Test leave-specific edge cases:
   - weekend exclusion
   - insufficient balance
   - overlapping pending requests
   - manager acting outside their department
   - admin overriding an already processed request
   - deactivating a user with pending requests
5. Review security controls and confirm that sensitive data, especially password hashes, is never returned.
6. Inspect frontend responsiveness and accessibility requirements.
7. Review documentation for setup, environment variables, deployment, test users, and limitations.
8. Assign a final score using the 1-7 scale and explain the decision with concrete evidence.

### What a Strong Response Should Demonstrate

A high-quality response should provide more than descriptions. It should include complete or near-complete files, clear module boundaries, working API flows, realistic data models, safe authentication, meaningful validation, readable UI components, and documentation that lets another developer run and evaluate the project.

The justification should compare responses directly, cite specific implementation evidence, identify missing requirements, explain tradeoffs, and end with a clear verdict.

## Comparison Result

The included `justification.md` evaluates two model responses:

- **Response A:** Strong architecture-level explanation, but mostly conceptual and not directly executable.
- **Response B:** Stronger practical implementation with schemas, middleware, route logic, dashboard code, CSV export, and README content.

Final verdict:

```text
Response B is better than Response A.
Likert Score: 6
```

## Known Limitations

- Public holiday handling is intentionally out of scope.
- Email notifications are not implemented.
- The reference implementation uses in-memory storage instead of MongoDB.
- The Python package is a benchmark reference, not a full MERN application.
- A production solution should still use the requested stack: React, Vite, Tailwind CSS, Express, MongoDB, Mongoose, JWT cookies, bcryptjs, express-validator, helmet, cors, and express-rate-limit.

## Repository Link

```text
https://github.com/Dev123dahiya/Prompt_Analysis
```
