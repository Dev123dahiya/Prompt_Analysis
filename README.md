# Prompt Analysis Benchmark

![Language](https://img.shields.io/badge/language-Python-blue)
![Benchmark](https://img.shields.io/badge/type-LLM%20coding%20benchmark-green)
![Domain](https://img.shields.io/badge/domain-Leave%20Management-orange)
![Status](https://img.shields.io/badge/status-complete-brightgreen)

## Project Overview

The Benchmark Repository includes a comprehensive benchmark set whcih will aid in evaluation of the efficiency of the LLM in performing a end-to-end coding task of the real world.The scope of the benchmark includes **Leave Management System** of a medium-sized company. The aim of benchmark test is to evaluate how well an LLM can comprehend the product requirements, perform business logic, practice security principles, create documentation for the deployment, and produce quality code.
## Links

| Resource | URL |
| --- | --- |
| GitHub Repository | `https://github.com/Dev123dahiya/Prompt_Analysis` |
| Live Deployment | `https://leave-request-management-system.vercel.app/` |

## Repository Contents

| Path | Description |
| --- | --- |
| `prompt.md` | Prompt written by me to make the response. |
| `justification.md` | Structured comparison framework and final verdict for Response A vs Response B. |
| `golden_response/` | Modular executable reference implementation for the core backend/domain behavior. |
| `golden_response/goldenresponse.md` | Best responce I got to do my project. |
| `README.md` | All the project overveiw and the evaluation criterias. |

## Repository Structure

```text
Prompt_Analysis/
|-- README.md
|-- prompt.md
|-- justification.md
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
| Employee | `dev@gmail.com` | `Password123!` |
| Manager | `khushi@gmail.com` | `Password123!` |
| Admin | `arun@gmail.com` | `Password123!` |

## Evaluation Methodology
Response solutions must be judged on the basis of implementation, completeness, correctness, maintainability, and the justification provided. The purpose of evaluation is not just to see that the response solution includes the required features, but whether such a solution would be possible to develop and implement.

### Scoring Rubric

| Category | Weight | What to Evaluate |
| --- | ---: | --- || Coverage of Requirements | 20% | Ensures all explicitly stated prompt requirements have been met, such as role dashboards, REST endpoints, leave policies, CSV files, validation, documentation, and deployment instructions. |
| Correctness of Functionality | 20% | Validates real-life business logic: weekday only day calculation, balance validation, overlapping pending leave prevention, department restriction for managers, admin overrides, and user deactivation management. |
| Backend Quality | 15% | Evaluates API design, express routing, mongoose schemas, indexes, middleware use, pagination, filters, error handling through JSON response format, and separation of concerns. |
| Security and Validation | 15% | Checks for password encryption, http-only cookies, secured cookies, cors headers, helmet, rate limiting, sanitizing user inputs, validating emails, and not leaking any private information. |
| Frontend Quality | 10% | Ensures role-based dashboard, responsiveness of the designs, modal working, accessibility of the controls, proper ARIA labeling, keyboard navigation, lazy loading of the routes, and search bar debounce. || Documentation and Deployment Readiness | 10% | Confirms that README is readable, installation process is possible locally, list of environment variables, seeding of database, authentication details, deployment on Vercel, Render, MongoDB Atlas, and constraints understanding. |
| Maintainability & Organization | 10% | Evaluates the code quality, modularity of the code, consistent variable names, comments in the code, proper handling of the errors, considerations for the edge cases, and extent of code maintainability. |
### Suggested Rating Scale

| Score | Meaning |
| --- | --- |
| 1 | The task cannot be accomplished satisfactorily by the process, being mostly useless or dysfunctional. |
| 2 | References are made to various requirements, yet without implementing any useful functionality. |
| 3 | Partial implementation is achieved, but vital steps in the workflow are missing or assumptions are dangerous. |
| 4 | The solution works functionally, but with significant limitations or lacking edge cases. |
| 5 | A satisfactory solution that satisfies the majority of the requirements, although not perfect. |
| 6 | An excellent solution, properly implemented, with a few minor flaws. |
| 7 | A production-level solution meeting all relevant requirements. |

### Evaluation Workflow

1. Read `prompt.md` and list all explicit constraints.
2. Check whether response provides is runnable code, not only an architecture description.
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
7. Review the documentation for setup, environment variables, deployment, test users.
8. Assign a final score between the 1-7 scale and explain the decision with concrete evidence and suitable facts.

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
## Repository Link

```text
https://github.com/Dev123dahiya/Prompt_Analysis
```
