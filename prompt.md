# Prompt

## Context

You are a senior full-stack developer with deep MERN-stack experience. Your task is to build a production-ready **Leave Management System** for a mid-sized organization.

The application must support three authenticated user roles:

- Employee
- Manager
- Admin

Each role must have a dedicated dashboard, role-specific navigation, and permissions appropriate to the user's responsibilities.

## Objective

Build a complete full-stack Leave Management System that supports:

- Secure JWT authentication using httpOnly cookies.
- Role-based dashboards for Employee, Manager, and Admin users.
- Employee leave request creation, viewing, editing, and cancellation.
- Manager approval and rejection workflows.
- Admin employee management, global policy configuration, and CSV reporting.
- Responsive, accessible UI suitable for mobile, tablet, and desktop.
- Clear local setup and deployment documentation.

## Explicit Constraints

The implementation must satisfy all of the following checkable constraints:

1. Use the specified MERN stack: React 18+, Vite, Tailwind CSS, Node.js 20+, Express, MongoDB, and Mongoose.
2. Implement every REST endpoint listed in the API Requirements section.
3. Count leave days using weekdays only, excluding Saturdays and Sundays.
4. Prevent employees from creating overlapping pending leave requests.
5. Enforce leave balances based on approved leave in the current calendar year.
6. Restrict managers to employees in their own department.
7. Store JWTs in secure httpOnly cookies and never return password hashes.
8. Provide a responsive and accessible UI using semantic HTML, ARIA labels, and keyboard-navigable controls.
9. Include complete README documentation for local setup, environment variables, deployment, test users, and known limitations.

## UI and Layout Requirements

### Global Layout

- After login, show only the dashboard, navigation options, and data available to the authenticated role.
- Use side navigation on desktop screens.
- Use bottom navigation on mobile screens.
- Provide a logout option from every dashboard.
- Use Tailwind CSS for responsive styling.
- Use semantic HTML and ARIA labels for interactive controls.

### Employee Dashboard

The Employee dashboard must include:

- Leave balance cards for annual, sick, and casual leave.
- A `Request Leave` button that opens a modal form.
- Modal fields:
  - leave type
  - start date
  - end date
  - optional reason
- A table of past requests with:
  - type
  - start date
  - end date
  - requested days
  - status
  - submitted date
  - actions
- Edit and delete icons shown only when the request status is `pending`.
- Edit behavior that reopens the modal with pre-filled data and revalidates leave balance.

### Manager Dashboard

The Manager dashboard must include:

- A list of leave requests from employees in the manager's department only.
- Approve and Reject buttons on each row.
- Disabled Approve and Reject buttons when the request status is not `pending`.
- A rejection modal that requires a comment of at least 5 characters.
- Filter tabs:
  - All
  - Pending
  - Approved
  - Rejected
- A debounced search box for employee name.

### Admin Dashboard

The Admin dashboard must use a tabbed interface with:

- User Management
- Policy Settings
- Report Generator

User Management must include:

- A table of all non-admin employees.
- Table columns:
  - name
  - email
  - department
  - role
  - active/inactive status
  - actions
- Edit and deactivate/reactivate actions.
- An `Add User` modal that collects:
  - name
  - email
  - department
  - role
  - start date

Policy Settings must include:

- Annual leave limit input with default value `20`.
- Sick leave limit input with default value `10`.
- Casual leave limit input with default value `5`.
- A save button that updates the global policy.

Report Generator must include:

- Start date and end date inputs.
- A `Download CSV` button.
- CSV output with these columns:
  - employee name
  - email
  - department
  - leave type
  - start date
  - end date
  - days
  - status
  - manager comment

## API Requirements

Implement all endpoints as RESTful JSON endpoints.

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| POST | `/api/auth/login` | Public | Login, return user info, and set an httpOnly JWT cookie |
| POST | `/api/auth/logout` | Authenticated | Clear the auth cookie |
| GET | `/api/leave/requests` | Employee/Manager/Admin | Return role-filtered leave requests with pagination and status filtering |
| POST | `/api/leave/request` | Employee | Create a leave request after balance and overlap validation |
| PUT | `/api/leave/request/:id` | Employee if pending | Edit an existing pending request |
| DELETE | `/api/leave/request/:id` | Employee if pending | Delete a pending request |
| PUT | `/api/leave/request/:id/status` | Manager/Admin | Approve or reject a request; rejection requires a comment |
| GET | `/api/leave/balance` | Employee | Return remaining days for each leave type |
| GET | `/api/admin/users` | Admin | List all employees, excluding admins |
| POST | `/api/admin/users` | Admin | Add a new employee |
| PUT | `/api/admin/users/:id` | Admin | Update or deactivate an employee |
| GET | `/api/admin/policy` | Admin | Return current leave policy limits |
| PUT | `/api/admin/policy` | Admin | Update leave policy limits |
| POST | `/api/admin/report` | Admin | Generate a CSV report for a date range |

## Data Processing Rules

- Leave days must count only Monday through Friday.
- Saturdays and Sundays must be excluded.
- Public holiday handling is out of scope for v1.
- Leave balance must be calculated as:

```text
policy limit - approved leave days of the same type in the current calendar year
```

- The current calendar year is January 1 through December 31.
- Employees cannot submit a request if requested days exceed the remaining balance for that leave type.
- Employees cannot have two pending requests with overlapping date ranges.
- Managers can only view and act on requests from employees in their own department.
- Admins can view and act on all requests.
- Admins can approve or reject any request, even if a manager has already acted on it.
- Manager comments must be preserved separately when an admin overrides a request.

## Validation and Security

- Sanitize all user inputs, including name, email, reason, and comment.
- Use `express-validator` or an equivalent validation layer.
- Validate email addresses with a standard validator.
- Hash passwords using `bcryptjs` with 10 salt rounds.
- Never include password hashes in API responses.
- Store JWTs in httpOnly cookies with:
  - `secure`
  - `sameSite=lax`
  - `maxAge=7 days`
- JWT payload must include:
  - userId
  - role
  - departmentId
- Rate-limit login to 5 attempts per 15 minutes per IP address.
- Rate-limit logout to 10 calls per hour per user.
- Enable Helmet security headers.
- Configure CORS to allow only the deployed frontend URL.

## Error Handling

Frontend errors must be user-friendly and must not expose technical internals.

Examples:

- `Not enough leave credits`
- `Conflict in request`
- `Bad credentials`

Backend errors must use this JSON shape:

```json
{
  "success": false,
  "message": "string",
  "code": "string",
  "errors": []
}
```

All backend errors must be logged with timestamps.

The implementation must explicitly handle:

- Manager attempts to approve a request from another department: return `403 Forbidden`.
- Employee attempts to modify an already approved or rejected request: return `403 Forbidden`.
- Admin deactivates a user with pending requests: reject the pending requests and document this behavior.

## Performance and Scalability

- Lazy-load route components using `React.lazy()`.
- Add MongoDB indexes on `userId`, `status`, and `departmentId`.
- Keep `GET /api/leave/requests` under 300ms for normal department-sized data.
- Debounce manager and admin search inputs.
- Avoid unnecessary React re-renders.
- Include a document title and meta description for basic SEO.

## Documentation Requirements

The README must include:

- Project overview.
- Folder structure as a text tree.
- Step-by-step local setup:
  - clone repository
  - install dependencies
  - configure `.env`
  - seed database
  - run frontend and backend
- Backend environment variable table.
- Frontend environment variable table.
- Deployment steps for:
  - Vercel frontend
  - Render backend
  - MongoDB Atlas database
- Test credentials for Employee, Manager, and Admin users.
- Known limitations, including no public holidays and no email notifications unless implemented as a bonus.

## Technology Stack

### Frontend

- React 18+ with Vite
- Tailwind CSS
- React Router 6
- Axios

### Backend

- Node.js 20+ with Express
- MongoDB with Mongoose
- JWT authentication using httpOnly cookies
- bcryptjs
- express-validator
- helmet
- cors
- express-rate-limit

### Deployment

- Frontend: Vercel
- Backend: Render
- Database: MongoDB Atlas
