# Golden Response — Leave Management System

## 1. Introduction

`golden_response.py` is a single-file Python implementation of a Leave Management System built with only the standard library. It combines authentication, authorization, leave workflows, validation, reporting, and a small HTTP API into one self-contained program.

The goal of the package is to provide a compact but complete reference implementation that can:

- run as a local API server,
- issue and verify signed session tokens,
- manage users and leave requests,
- enforce role-based access,
- validate and sanitize incoming data,
- generate a CSV report,
- and run a built-in self-test.

---

## 2. High-Level Architecture

The application is organized logically into these parts:

1. **Configuration**
   - Shared constants for secret key, token lifetime, date format, roles, and leave types.

2. **Error Handling**
   - A structured `ApiError` exception that returns consistent API responses.

3. **Data Models**
   - Dataclasses for `User`, `LeaveRequest`, and `Policy`.

4. **Validation**
   - Helpers for sanitizing text, validating email addresses, parsing dates, enforcing date order, and checking weekdays.

5. **Security**
   - Password hashing using PBKDF2-HMAC.
   - Signed token creation and verification using HMAC.
   - Simple in-memory rate limiting.

6. **Business Service**
   - The `LeaveManagementService` class, which contains all main leave-management logic.

7. **HTTP Server**
   - A standard-library `BaseHTTPRequestHandler` wrapper that exposes REST-like endpoints.

8. **Testing**
   - A built-in `run_self_test()` function for quick verification.

9. **CLI Entry Point**
   - A command-line interface that can start the server or run the self-test.

---

## 3. Core Capabilities

### Authentication
The system supports login using email and password. On success, it creates a signed token and sends it back as an HTTP cookie.

### Authorization
Role-based access control is enforced for:

- `employee`
- `manager`
- `admin`

### Leave Requests
Employees can create leave requests, edit pending requests, delete pending requests, and view their own request history.

### Manager Workflow
Managers can review leave requests from their department and approve or reject them with comments.

### Admin Workflow
Admins can view and manage all users, update leave policy values, generate reports, and override request status.

### Reporting
A CSV report can be generated for requests inside a date range.

### Security Controls
The code includes:

- password hashing,
- signed token handling,
- token expiry,
- input sanitization,
- and request throttling.

---

## 4. File-Level Breakdown

Even though the final deliverable is a single file, the logic is conceptually split into modules.

### 4.1 Configuration
This section stores application-wide constants:

- `SECRET_KEY`
- `TOKEN_TTL_SECONDS`
- `DATE_FORMAT`
- `LEAVE_TYPES`
- `ROLES`

These constants keep validation and security behavior consistent across the codebase.

### 4.2 Error Handling
`ApiError` is the custom exception type used throughout the application.

It includes:

- HTTP status code,
- human-readable message,
- machine-readable error code,
- optional validation errors.

Every error response is shaped in a predictable JSON format.

### 4.3 Models
The data model layer includes:

#### `User`
Represents an employee, manager, or admin.

Fields include:

- id
- name
- email
- department_id
- role
- start_date
- password_hash
- active

#### `LeaveRequest`
Represents one leave application.

Fields include:

- id
- user_id
- leave_type
- start_date
- end_date
- days
- reason
- status
- submitted_at
- manager_comment
- admin_comment
- decided_by

#### `Policy`
Stores yearly leave quota values for each leave type.

Fields include:

- annual
- sick
- casual

---

## 5. Validation Logic

Validation is performed before values are stored or processed.

### `sanitize_text`
- Ensures a value is text.
- Trims whitespace.
- Escapes HTML.
- Removes control characters.
- Enforces required fields and length limits.

### `sanitize_email`
- Normalizes email to lowercase.
- Validates email format using a regular expression.

### `sanitize_choice`
- Converts input to lowercase.
- Ensures the value is one of the allowed options.

### `parse_date`
- Parses dates in `YYYY-MM-DD` format.

### `ensure_date_order`
- Prevents end dates earlier than start dates.

### `weekday_count`
- Counts only Monday to Friday.
- Used to calculate leave days.

### `positive_int`
- Ensures a number is between 0 and 365.

### `require_role`
- Ensures the active user has permission to access a feature.

---

## 6. Security Design

### Password Hashing
Passwords are not stored in plain text. They are hashed using PBKDF2-HMAC-SHA256 with a random salt.

### Token Issuance
Tokens are signed using HMAC with a secret key. Each token contains:

- user ID
- role
- department ID
- expiration time

### Token Verification
When a token is received:

1. The signature is checked.
2. The payload is decoded.
3. The expiry time is verified.

If anything fails, the request is rejected.

### Rate Limiting
A simple in-memory rate limiter protects login and logout behavior from abuse.

---

## 7. Business Logic in `LeaveManagementService`

The `LeaveManagementService` class is the heart of the application.

### 7.1 Initialization
When the service starts:

- it creates the default leave policy,
- initializes in-memory users and requests,
- sets up counters for IDs,
- creates the rate limiter,
- and seeds sample users.

### 7.2 Seed Users
The system starts with three built-in users:

- an employee,
- a manager,
- an admin.

This makes local testing easier.

### 7.3 Adding Users
`add_user()` creates a new user after validating:

- name,
- email,
- department,
- role,
- and start date.

It also blocks duplicate email addresses.

### 7.4 Authentication
`authenticate()` checks email and password, applies rate limiting, and returns the user plus a signed token.

### 7.5 Logout
`logout()` applies a simple rate-limit check. In a real production system, token revocation would be more advanced, but here the behavior is intentionally lightweight.

### 7.6 User Lookup
`get_user()` returns an active user or raises an error.

### 7.7 Listing Leave Requests
`list_requests()` returns requests based on the actor’s role:

- employees see their own requests,
- managers see requests in their department,
- admins see all requests.

It also supports:

- status filtering,
- pagination,
- name search.

### 7.8 Creating Leave Requests
`create_request()`:

- allows only employees,
- validates payload values,
- counts weekdays,
- checks for overlapping pending requests,
- checks leave balance,
- stores the request.

### 7.9 Editing Leave Requests
`edit_request()`:

- allows only employees,
- allows only pending requests,
- re-validates the payload,
- checks overlaps and balance again.

### 7.10 Deleting Leave Requests
`delete_request()`:

- allows only employees,
- allows only pending requests,
- removes the request from storage.

### 7.11 Updating Request Status
`update_status()` allows managers and admins to approve or reject requests.

Behavior differs by role:

#### Manager
- Can only process requests for their own department.
- Can only process pending requests.
- Stores the manager comment.

#### Admin
- Can override requests.
- Stores the admin comment.

### 7.12 Leave Balance
`get_balance()` returns remaining leave credits for an employee.

### 7.13 User Management
Admins can:

- list users,
- update a user,
- deactivate a user.

When a user is deactivated, their pending leave requests are automatically rejected.

### 7.14 Policy Management
Admins can update leave quotas.

### 7.15 Reporting
`generate_report()` creates a CSV report for requests inside a given date range.

The report includes columns such as:

- employee name,
- email,
- department,
- leave type,
- start and end dates,
- number of days,
- status,
- manager comment.

---

## 8. HTTP API

The server is implemented with the Python standard library using `BaseHTTPRequestHandler`.

### 8.1 Available Methods
The API supports:

- `GET`
- `POST`
- `PUT`
- `DELETE`

### 8.2 Routes

#### Authentication
- `POST /api/auth/login`
- `POST /api/auth/logout`

#### Leave Requests
- `GET /api/leave/requests`
- `POST /api/leave/request`
- `PUT /api/leave/request/{id}`
- `DELETE /api/leave/request/{id}`
- `PUT /api/leave/request/{id}/status`
- `GET /api/leave/balance`

#### Admin
- `GET /api/admin/users`
- `POST /api/admin/users`
- `PUT /api/admin/users/{id}`
- `GET /api/admin/policy`
- `PUT /api/admin/policy`
- `POST /api/admin/report`

### 8.3 Response Format
Successful responses are generally JSON and include a `success` field.

Example structure:

```json
{
  "success": true,
  "data": {}
}
```

Error responses use the structured `ApiError` format.

---

## 9. Request Flow

### Login Flow
1. User sends email and password.
2. System validates credentials.
3. A signed token is issued.
4. Token is placed in a secure cookie.

### Leave Application Flow
1. Employee submits leave form.
2. Input is sanitized and validated.
3. Weekdays are counted.
4. Overlap and balance checks are performed.
5. Request is stored with `pending` status.

### Approval Flow
1. Manager or admin loads request.
2. System verifies permission.
3. Request status is updated.
4. Comment is saved.
5. Decision maker ID is recorded.

### Reporting Flow
1. Admin submits start and end dates.
2. System validates date range.
3. Requests in range are written to CSV.
4. CSV is returned as plain text.

---

## 10. Built-In Testing

The `run_self_test()` function checks key behaviors automatically.

It verifies that:

- login works,
- leave creation works,
- overlap detection works,
- approval updates balance,
- admin override comments are preserved,
- CSV reports are generated,
- user deactivation rejects pending requests.

This gives a quick sanity check before deployment or local execution.

---

## 11. CLI Usage

The program can be launched from the command line.

### Run Self-Test
```bash
python golden_response.py --self-test
```

### Start Server
```bash
python golden_response.py --serve --port 8000
```

### Show Help
```bash
python golden_response.py
```

---

## 12. Design Strengths

### Single-File Simplicity
The entire system is easy to inspect, distribute, and run.

### Clear Separation of Responsibility
Even in one file, the code is organized logically into configuration, models, validation, security, service, server, and tests.

### Security Consciousness
The code avoids plain-text password storage and uses signed tokens.

### Strong Validation
Inputs are checked carefully before being accepted.

### Role-Based Controls
Access is explicitly restricted by role.

### Testability
The self-test function makes correctness easier to verify.

---

## 13. Limitations

This implementation is intentionally minimal and uses in-memory storage.

That means:

- data is lost when the process stops,
- there is no real database,
- there is no distributed session store,
- token revocation is limited,
- and concurrency persistence is not production-grade.

It is best treated as a reference or benchmark implementation rather than a full enterprise deployment.

---

## 14. Suggested Future Improvements

Possible enhancements include:

- database persistence,
- refresh tokens,
- stronger revocation support,
- audit logging,
- email notifications,
- frontend integration,
- exports in additional formats,
- more granular permissions,
- and comprehensive automated tests.

---

## 15. Summary

`golden_response.py` is a compact but complete leave management backend that demonstrates:

- secure authentication,
- permissions-based access,
- validated leave workflows,
- admin and manager actions,
- report generation,
- and runnable self-tests.

It is a good example of how a complete business system can be implemented cleanly in one Python file while still remaining readable and structured.
