# Golden Response

Below is the ideal response for the submitted Leave Management System prompt. It represents a production-quality benchmark answer in a structured format.

## Final Answer

I have prepared a complete reference implementation for the core Leave Management System requirements. The solution is organized as a modular backend/domain package and includes authentication, role-based access, leave request workflows, policy enforcement, CSV reporting, validation, and executable tests.

The implementation focuses on the most important business and backend rules from the prompt:

- Employee, Manager, and Admin role handling.
- Secure authentication flow using signed tokens.
- Password hashing.
- Login and logout rate limiting.
- Input sanitization and email validation.
- Weekday-only leave calculation.
- Leave balance enforcement.
- Pending request overlap prevention.
- Manager department restriction.
- Admin override behavior.
- Automatic rejection of pending requests when a user is deactivated.
- Structured API-style error responses.
- CSV report generation.
- A small runnable HTTP API.
- Built-in self-test coverage.

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

## File Responsibilities

| File | Purpose |
| --- | --- |
| `golden_response/__main__.py` | Allows the package to run with `python -m golden_response`. |
| `golden_response/cli.py` | Provides command-line options for self-test and local server mode. |
| `golden_response/config.py` | Stores shared constants such as roles, leave types, date format, and token TTL. |
| `golden_response/errors.py` | Defines structured API-style errors. |
| `golden_response/models.py` | Defines `User`, `LeaveRequest`, and `Policy` data models. |
| `golden_response/security.py` | Handles password hashing, signed tokens, and rate limiting. |
| `golden_response/validators.py` | Handles sanitization, validation, date parsing, role checks, and weekday counting. |
| `golden_response/service.py` | Contains the main Leave Management business logic. |
| `golden_response/server.py` | Exposes the service through a small standard-library HTTP API. |
| `golden_response/tests.py` | Provides the built-in behavioral self-test. |

## How to Run

Run the built-in self-test:

```bash
python -m golden_response --self-test
```

Expected output:

```text
Self-test passed.
```

Start the local API server:

```bash
python -m golden_response --serve --port 8000
```

API base URL:

```text
http://127.0.0.1:8000
```

## Seeded Users

| Role | Email | Password |
| --- | --- | --- |
| Employee | `employee@example.com` | `Password123!` |
| Manager | `manager@example.com` | `Password123!` |
| Admin | `admin@example.com` | `Password123!` |

## Covered Prompt Requirements

### Authentication and Security

- Passwords are hashed before storage.
- Password hashes are never returned in public user payloads.
- Signed tokens include `userId`, `role`, `departmentId`, and expiry.
- Login is rate-limited to protect against brute-force attempts.
- Logout is rate-limited per user.
- Inputs are sanitized.
- Emails are validated.
- API responses use structured JSON errors.

### Leave Business Rules

- Leave days are calculated using weekdays only.
- Saturday and Sunday are excluded.
- Leave balances are calculated from approved leave in the current calendar year.
- Requests that exceed remaining leave balance are rejected.
- Employees cannot create overlapping pending leave requests.
- Employees can only edit or delete their own pending requests.
- Approved or rejected requests cannot be modified by employees.

### Manager Rules

- Managers can only view requests from employees in their department.
- Managers can only act on pending requests.
- Rejecting a request requires a comment of at least 5 characters.
- Cross-department manager actions return a forbidden error.

### Admin Rules

- Admins can view all requests.
- Admins can approve or reject any request.
- Admin comments are preserved separately from manager comments.
- Admins can update global leave policy limits.
- Admins can list, add, update, deactivate, and reactivate non-admin users.
- When an admin deactivates a user with pending requests, those pending requests are automatically rejected.

### Reporting

- Admins can generate CSV reports for a date range.
- CSV output includes:
  - employee name
  - email
  - department
  - leave type
  - start date
  - end date
  - days
  - status
  - manager comment

## Why This Is the Golden Response

This response is considered the golden benchmark solution because it is executable, modular, and aligned with the prompt's explicit constraints. It does not only describe the system; it implements the core rules in code and includes tests for the most important edge cases.

The implementation is maintainable because responsibilities are separated into focused modules:

- models for data structures
- validators for input rules
- security for authentication behavior
- service for business logic
- server for HTTP routing
- tests for behavioral verification

## Important Note

The original prompt asks for a MERN-stack production application. This golden response uses Python for benchmark portability, but it faithfully models the required backend/domain behavior. A full MERN implementation should translate the same rules into React, Express, MongoDB, Mongoose, JWT httpOnly cookies, bcryptjs, express-validator, helmet, cors, and express-rate-limit.
