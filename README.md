# Prompt Analysis Benchmark

![Language](https://img.shields.io/badge/language-Python-blue)
![Benchmark](https://img.shields.io/badge/type-LLM%20coding%20benchmark-green)
![Domain](https://img.shields.io/badge/domain-Leave%20Management-orange)

This repository contains a complete LLM benchmark package for evaluating responses to a domain-specific full-stack coding task.

The benchmark focuses on a **Leave Management System** for a mid-sized company. It tests whether an LLM can understand realistic product requirements, implement business rules, reason about security, and produce maintainable production-style code.

## What This Repository Includes

| File | Purpose |
| --- | --- |
| `prompt.md` | The original coding prompt given to an LLM. |
| `justification.md` | A structured comparison framework for evaluating Response A and Response B. |
| `golden_response/` | A structured executable reference solution for the core backend/domain logic. |
| `golden_response.py` | Compatibility launcher for the structured golden response package. |
| `README.md` | Project overview, run instructions, and evaluation methodology. |

## Repository Structure

```text
Prompt_Analysis/
|-- prompt.md
|-- justification.md
|-- golden_response.py
|-- golden_response/
|   |-- __main__.py
|   |-- cli.py
|   |-- config.py
|   |-- errors.py
|   |-- models.py
|   |-- security.py
|   |-- server.py
|   |-- service.py
|   |-- tests.py
|   `-- validators.py
`-- README.md
```

## Benchmark Overview

The prompt asks an LLM to build a MERN-stack Leave Management System with:

- Employee, Manager, and Admin roles.
- Secure JWT authentication.
- Role-based dashboards.
- Leave request creation, editing, cancellation, approval, and rejection.
- Leave balance enforcement.
- Weekday-only leave calculation.
- Pending request overlap prevention.
- Department-restricted manager permissions.
- Admin policy configuration.
- CSV report generation.
- Responsive, accessible frontend requirements.
- Deployment documentation for Vercel, Render, and MongoDB Atlas.

## Golden Response

`golden_response/` is a modular Python reference implementation. It is not intended to replace the requested MERN stack application. Instead, it provides an executable benchmark solution for the most important backend and business-rule behavior.

It includes:

- Authentication with signed tokens.
- Password hashing.
- Login and logout rate limiting.
- Structured API-style error responses.
- Input sanitization and email validation.
- Weekday-only leave day calculation.
- Balance checks against annual, sick, and casual leave policies.
- Pending request overlap detection.
- Manager department authorization.
- Admin override behavior.
- User deactivation handling.
- CSV report generation.
- A small HTTP API using the Python standard library.
- Built-in self-test coverage for the main edge cases.

## How to Run

The golden response uses only the Python standard library.

Run the built-in self-test:

```bash
python -m golden_response --self-test
```

The root launcher also works:

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

## Test Credentials

| Role | Email | Password |
| --- | --- | --- |
| Employee | `employee@example.com` | `Password123!` |
| Manager | `manager@example.com` | `Password123!` |
| Admin | `admin@example.com` | `Password123!` |

## Evaluation Methodology

Responses should be evaluated on both implementation quality and justification quality.

Primary evaluation criteria:

- **Requirement coverage:** Does the response satisfy the explicit prompt constraints?
- **Executability:** Can the submitted code run with clear setup instructions?
- **Business logic correctness:** Are leave balances, overlaps, weekday calculations, and role permissions handled correctly?
- **Security:** Are authentication, password handling, validation, cookies, CORS, rate limits, and error messages implemented safely?
- **Frontend quality:** Are dashboards responsive, accessible, role-aware, and user-friendly?
- **Backend quality:** Are APIs RESTful, structured, validated, and maintainable?
- **Documentation:** Are setup, environment variables, deployment steps, test credentials, and limitations explained clearly?
- **Maintainability:** Is the code readable, modular, properly named, and easy to extend?

## Comparison Summary

The included `justification.md` compares two model responses:

- **Response A:** Strong architectural explanation, but mostly conceptual and not directly executable.
- **Response B:** Stronger practical implementation with schemas, middleware, routes, dashboard code, CSV export, and README content.

Final verdict:

```text
Response B is better than Response A.
Likert Score: 6
```

## Known Limitations

- Public holiday handling is not included.
- Email notifications are not included.
- The golden response uses in-memory storage instead of MongoDB.
- The Python package is a benchmark reference, not a full MERN deployment.
- A production implementation should still use the requested stack: React, Vite, Tailwind CSS, Express, MongoDB, Mongoose, JWT httpOnly cookies, bcryptjs, express-validator, helmet, cors, and express-rate-limit.

## Submission Link

GitHub repository:

```text
https://github.com/Dev123dahiya/Prompt_Analysis
```
