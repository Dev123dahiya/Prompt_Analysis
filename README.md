# Prompt Analysis Benchmark

![Language](https://img.shields.io/badge/language-Python-blue)
![Benchmark](https://img.shields.io/badge/type-LLM%20coding%20benchmark-green)
![Domain](https://img.shields.io/badge/domain-Leave%20Management-orange)
![Status](https://img.shields.io/badge/status-complete-brightgreen)

## Project Overview

This repository contains a complete benchmark package for evaluating LLM responses to a realistic, domain-specific full-stack coding task.

The benchmark is centered on a **Leave Management System** for a mid-sized organization. It tests whether an LLM can interpret detailed product requirements, implement business rules, apply security best practices, document setup and deployment, and produce maintainable production-style code.

## Repository Contents

| Path | Description |
| --- | --- |
| `prompt.md` | Original MERN-stack coding prompt used for evaluation. |
| `justification.md` | Structured comparison framework and final verdict for Response A vs Response B. |
| `golden_response.py` | Root-level launcher required by the submission checklist. |
| `golden_response/` | Modular executable reference implementation for the core backend/domain behavior. |
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

Responses should be evaluated on implementation quality, requirement coverage, and the quality of the accompanying justification.

| Criterion | What to Check |
| --- | --- |
| Requirement coverage | All explicit UI, API, security, data-processing, and documentation constraints are addressed. |
| Executability | Code can be run or integrated with clear setup instructions. |
| Business logic | Leave balances, weekday counting, overlap prevention, admin override, and manager restrictions are correct. |
| Security | Authentication, password hashing, validation, cookies, CORS, rate limits, and error handling are implemented safely. |
| Frontend quality | Dashboards are role-aware, responsive, accessible, and easy to use. |
| Backend quality | APIs are RESTful, validated, structured, and maintainable. |
| Documentation | Setup, environment variables, deployment, test credentials, and limitations are clearly documented. |
| Maintainability | Code is readable, modular, consistently named, and easy to extend. |

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
