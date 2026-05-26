# Golden Response Package

This folder contains the modular reference implementation for the Leave Management System benchmark.

## Structure

```text
golden_response/
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

## Module Guide

| File | Responsibility |
| --- | --- |
| `cli.py` | Command-line entry point for self-test and local API server. |
| `config.py` | Shared constants such as token TTL, roles, and leave types. |
| `errors.py` | Structured API error class. |
| `models.py` | Dataclasses for users, leave requests, and policy. |
| `security.py` | Password hashing, signed tokens, and rate limiting. |
| `validators.py` | Input sanitization, date parsing, role checks, and weekday counting. |
| `service.py` | Core leave-management business logic. |
| `server.py` | Standard-library HTTP API wrapper. |
| `tests.py` | Built-in behavioral self-test. |

## Run

From the repository root:

```bash
python -m golden_response --self-test
python -m golden_response --serve --port 8000
```
