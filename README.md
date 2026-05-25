# Prompt Analysis Benchmark

This repository contains a benchmark prompt, an evaluation framework, and a golden reference implementation for a domain-specific Leave Management System task.

The benchmark asks an LLM to design and implement a MERN-stack leave management platform for a mid-sized firm. The system includes Employee, Manager, and Admin workflows, role-based authorization, leave balance enforcement, overlap prevention, policy management, CSV reporting, and production-oriented security requirements.

## Repository Structure

```text
.
├── prompt.md
├── justification.md
├── golden_response.py
└── README.md
```

## Files

- `prompt.md` contains the original domain-specific coding prompt.
- `justification.md` contains the side-by-side evaluation framework and final verdict comparing Response A and Response B.
- `golden_response.py` contains a single-file executable reference implementation of the core backend/domain behavior.
- `README.md` explains how to run the benchmark reference and how the evaluation methodology works.

## Running the Golden Response

The golden response uses only the Python standard library.

```bash
python golden_response.py --self-test
```

Expected output:

```text
Self-test passed.
```

To start the local reference API:

```bash
python golden_response.py --serve --port 8000
```

The server runs at:

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

Responses should be evaluated against the prompt using these criteria:

- Completeness of role-based Employee, Manager, and Admin workflows.
- Correct implementation of leave business rules, including weekday-only counting, balance enforcement, and overlap prevention.
- Security posture, including password hashing, JWT cookie authentication, input validation, rate limiting, Helmet-style headers, and CORS restrictions.
- API correctness, including RESTful routes, role-filtered data, structured JSON errors, and CSV report generation.
- Frontend quality, including responsive layout, accessibility, dashboard-specific UI, and debounced search.
- Maintainability, including clean structure, readable code, proper error handling, indexes, and deployment documentation.

The provided `justification.md` demonstrates a structured comparison between two model responses. It gives a final verdict, side-by-side analysis, and strengths and weaknesses for both responses.

## Notes on the Golden Response

`golden_response.py` is intentionally a single executable Python file for benchmark portability. It models the core behavior required by the prompt in a way that can be run and tested immediately.

A full production answer to `prompt.md` should implement the same rules using the requested MERN stack: React, Vite, Tailwind CSS, Node.js, Express, MongoDB, Mongoose, JWT httpOnly cookies, bcryptjs, express-validator, helmet, cors, and express-rate-limit.

## Known Limitations

- Public holiday handling is not included.
- Email notifications are not included.
- The single-file golden response uses in-memory storage rather than MongoDB.
- The single-file golden response is a benchmark reference, not a complete deployed MERN application.
