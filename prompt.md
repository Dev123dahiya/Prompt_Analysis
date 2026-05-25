# Prompt

## Context and Role

You are a senior full-stack developer specializing in the MERN stack. Build a robust Leave Management System for a mid-sized firm with three authenticated role profiles: Employee, Manager, and Admin. Each role must have a dedicated dashboard and role-specific permissions for leave processing, balance management, employee management, policy management, and reporting.

## Objective

Build a complete full-stack Leave Management System that supports:

- Role-based dashboards with secure JWT authentication.
- Employees can create, read, edit only pending, cancel only pending, and view available leave.
- Managers can approve or reject leave applications from employees in their department, with optional comments for approvals and required comments for rejections.
- Admins can create, edit, and deactivate employee accounts, configure global leave policy, and export reports in CSV format.
- The application must be responsive, accessible, and deployable.

## UI and Layout Requirements

### Role-Based Dashboard

- After successful authentication, display only the navigation options and data available to the authenticated role.
- Use side navigation on desktop and bottom navigation on mobile.
- Provide a logout option from every dashboard.

### Employee Dashboard

- Display remaining leave balance for annual, sick, and casual leave as cards.
- A `Request Leave` button must open a modal form with leave type, start date, end date, and optional reason fields.
- Show a table of past requests with type, start date, end date, requested days, status, submitted date, and actions.
- Edit and delete icons must appear only when status is `pending`.
- Editing a request must reopen the modal with pre-filled data and revalidate leave balance.

### Manager Dashboard

- Show leave requests from employees in the manager's department only.
- Each row must have Approve and Reject buttons.
- Approve and Reject buttons must be disabled unless the request status is `pending`.
- Rejection must open a modal requiring a comment of at least 5 characters.
- Provide filter tabs: All, Pending, Approved, Rejected.
- Provide a debounced search box by employee name.

### Admin Dashboard

Use a tabbed interface with:

- User Management
- Policy Settings
- Report Generator

User Management must include:

- A table of all non-admin employees with columns for name, email, department, role, active/inactive status, and actions.
- Edit and deactivate/reactivate actions.
- An `Add User` modal that collects name, email, department, role, and start date.

Policy Settings must include:

- Number inputs for annual leave limit, default `20`.
- Number inputs for sick leave limit, default `10`.
- Number inputs for casual leave limit, default `5`.
- A save button that updates the global policy.

Report Generator must include:

- Start and end date range picker.
- `Download CSV` button that calls the backend.
- CSV columns: employee name, email, department, leave type, start date, end date, days, status, manager comment.

## Layout Constraints

- Fully responsive for mobile, tablet, and desktop using Tailwind CSS.
- Accessible with semantic HTML, ARIA labels, and keyboard-navigable controls.
- Optimized for performance with lazy-loaded routes and no unnecessary re-renders.

## Backend Requirements

Implement all endpoints as RESTful JSON endpoints.

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| POST | `/api/auth/login` | Public | Login, return user info, and set an httpOnly JWT cookie |
| POST | `/api/auth/logout` | Authenticated | Clear the auth cookie |
| GET | `/api/leave/requests` | Employee/Manager/Admin | Return role-filtered leave list with pagination and status filtering |
| POST | `/api/leave/request` | Employee | Create leave request after balance and overlap validation |
| PUT | `/api/leave/request/:id` | Employee if pending | Edit an existing pending request |
| DELETE | `/api/leave/request/:id` | Employee if pending | Delete a pending request |
| PUT | `/api/leave/request/:id/status` | Manager/Admin | Approve or reject a request; rejection requires comment |
| GET | `/api/leave/balance` | Employee | Return remaining days for each leave type |
| GET | `/api/admin/users` | Admin | List all employees, excluding admins |
| POST | `/api/admin/users` | Admin | Add a new employee |
| PUT | `/api/admin/users/:id` | Admin | Update or deactivate an employee |
| GET | `/api/admin/policy` | Admin | Return current leave policy limits |
| PUT | `/api/admin/policy` | Admin | Update leave policy limits |
| POST | `/api/admin/report` | Admin | Generate a CSV report for a given date range |

## Data Processing Requirements

- Leave days calculation must count weekdays only, Monday through Friday. Saturdays and Sundays are excluded. Public holidays are out of scope for v1.
- Balance equals policy limit minus approved leave days of the same type in the current calendar year, January 1 through December 31.
- Employees cannot submit leave requests that exceed the remaining balance for the selected leave type.
- Employees cannot have two pending requests with overlapping date ranges.
- Managers can only see and act on requests for employees in their own department.
- Admins can see and act on all requests.
- Admins can approve or reject any request, even if a manager has already acted on it.
- Preserve the manager's comment separately when an admin overrides a request.

## Validation and Security

- Sanitize all user input, including name, email, reason, and comment, to prevent XSS and injection attacks.
- Use `express-validator` or an equivalent validation layer.
- Validate emails using a standard validator.
- Hash passwords using `bcryptjs` with 10 salt rounds.
- Never return password hashes from any API response.
- Store JWTs in httpOnly cookies with `secure`, `sameSite=lax`, and `maxAge=7 days`.
- JWT payload must include userId, role, and departmentId.
- Rate-limit login to 5 attempts per 15 minutes per IP address.
- Rate-limit logout to 10 calls per hour per user.
- Enable Helmet.
- Configure CORS to allow only the frontend URL.

## Error Handling

Frontend errors must be user-friendly, such as:

- `Not enough leave credits`
- `Conflict in request`
- `Bad credentials`

Backend errors must use:

```json
{
  "success": false,
  "message": "string",
  "code": "string",
  "errors": []
}
```

All backend errors must be logged with timestamps.

The implementation must handle:

- Manager attempts to approve a request from another department: return `403 Forbidden`.
- Employee attempts to modify an approved request: return `403 Forbidden`.
- Admin deactivates a user with pending requests: reject the pending requests and document that behavior.

## README Requirements

The README must include:

- Folder structure as a text tree.
- Step-by-step local setup: clone, install, `.env`, seed database.
- Backend and frontend environment variable tables.
- Deployment steps for Vercel frontend and Render backend.
- Test credentials for employee, manager, and admin.
- Known limitations, including no public holidays and no email notifications unless implemented as a bonus.

## Performance and Scalability

- Lazy-load route components with `React.lazy()`.
- Add database indexes on `userId`, `status`, and `departmentId`.
- Keep `GET /api/leave/requests` under 300ms for normal department-sized data.
- Debounce search inputs in manager and admin dashboards.
- Include accessibility metadata and basic SEO with document title and meta description.

## Technology Stack

### Frontend

- React 18+ with Vite
- Tailwind CSS
- React Router 6
- Axios

### Backend

- Node.js 20+ with Express
- MongoDB and Mongoose
- JWT in httpOnly cookie
- bcryptjs
- express-validator
- helmet
- cors
- express-rate-limit

### Deployment

- Frontend: Vercel
- Backend: Render
- Database: MongoDB Atlas
