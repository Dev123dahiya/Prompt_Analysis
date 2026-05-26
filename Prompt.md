# **Context and Role**

As a Senior Full Stack Developer specialized in enterprise-grade SaaS applications, you are given the responsibility of designing and developing a complete production-ready Leave Management System . The system must automate the employee leave workflows, approval processes of leave, tracking of leave ,  reporting, and administrative management while maintaining high performance, scalability, security, accessibility, and maintainability.

The application must follow all the  software engineering standards.The final system should feel like a real-world HRMS platform used inside large organizations instead of a simple academic project.

The project must strictly follow:

* Clean architecture principles  
* Scalable folder structures  
* Modular backend development  
* Reusable frontend components  
* Production-grade API design  
* Secure authentication and authorization  
* Centralized validation systems  
* Structured error handling  
* Logging and monitoring  
* Performance optimization  
* Accessibility standards  
* Deployment readiness  
* Enterprise-level security practices

The final application should be suitable for:

* Real-world company usage  
* SaaS-style HRMS systems  
* Startup MVPs  
* Enterprise demonstrations  
* Portfolio projects  
* Internship showcases  
* Production-grade deployments  
  ---

  # **Objective**

Develop a complete full-stack project named as the Leave Management System that will allow employees to apply for leave, also the  managers to approve or reject requests for those leave, and administrators to manage company leave policies, their records, and organization-wide leave operations efficiently.

The system must:

* Allow secure employee registration and authentication  
* Allow admins to manage employees, policies, and departments  
* Automatically calculate leave balances  
* Maintain leave histories and audit logs  
* Provide notifications and real-time updates  
* Generate reports and analytics  
* Support future scalability

The final application must include:

* Authentication system  
* Role-based authorization  
* Employee dashboard  
* Manager dashboard  
* Admin dashboard  
* Leave request workflow  
* Leave approval workflow  
* Leave balance management  
* Notification system  
* Analytics and reporting  
* Audit logging system  
* File upload support  
* Secure REST APIs  
* Centralized validation system  
* Production-level error handling  
* Responsive and accessible UI  
* Scalable backend architecture  
  ---

# **UI and Animation Requirements**

The user interface must be modern, responsive, professional, and optimized for user experience across:

* Mobile devices  
* Tablets  
* Laptops  
* Desktop screens

The UI should include:

* Responsive layouts  
* Modern dashboards  
* Professional sidebar navigation  
* Analytics cards  
* Interactive charts  
* Search and filtering systems  
* Pagination  
* Loading states  
* Empty states  
* Confirmation dialogs  
* Toast notifications  
* Inline validation messages  
* Responsive tables  
* Accessible form components  
* Smooth navigation transitions

The UI should feel clean and enterprise-grade similar to modern SaaS HR platforms.

Animations and transitions should include:

* Smooth page transitions  
* Modal animations  
* Sidebar transition animations  
* Hover interactions  
* Button animations  
* Smooth dropdown interactions  
* Loading animations  
* Notification animations

Animation implementation rules:

* Use lightweight animations  
* Avoid layout thrashing  
* Use GPU-friendly properties  
* Avoid blocking rendering  
* Maintain smooth scrolling performance  
* Support low-end devices

Accessibility implementation must include:

* Semantic HTML  
* Proper ARIA labels  
* Keyboard navigation support  
* Screen reader compatibility  
* Visible focus indicators  
* Proper contrast ratios  
* Accessible forms and modals  
  ---

# **Architecture and Development Rules**

The application must follow a clean and scalable architecture pattern.

The architecture must implement:

* Separation of concerns  
* Reusable component architecture  
* Modular backend structure  
* Service-based architecture  
* Centralized error handling  
* Centralized validation systems  
* Reusable middleware structure  
* Reusable utilities  
* Reusable hooks  
* Shared validation schemas  
* Configuration management

Business logic must never be placed directly inside:

* Routes  
* Controllers  
* UI components

The backend architecture should follow:

* Controller-Service-Repository pattern  
* Modular route structure  
* Middleware-based request processing  
* Utility helper organization

The codebase must remain:

* Scalable  
* Maintainable  
* Reusable  
* Easy to debug  
* Easy to extend  
  ---
# **User Roles and Permissions**

## **1\. Employee**

Employees should be able to:

* Register and log in securely  
* Update personal profile information  
* Apply for leave  
* Edit pending leave requests  
* Cancel leave requests  
* Track leave request status  
* View leave balances  
* View leave history  
* Receive notifications  
* Download leave summaries if permitted

Employees must not be able to:

* Approve leave requests  
* Access admin dashboards  
* Modify leave policies  
* Access records of other employees  
* Modify approval workflows  
  ---
## **2\. Manager**

Managers should be able to:

* View leave requests from team members  
* Approve leave requests  
* Reject leave requests  
* Add approval comments  
* Add rejection comments  
* View department leave summaries  
* Monitor pending approvals  
* Access department reports

Managers must not be able to:

* Modify system-wide settings  
* Access super admin-only tools  
* Change authentication configurations  
  ---

## **3\. HR / Admin**

Admins should be able to:

* Manage employee records  
* Add employees  
* Edit employees  
* Remove employees  
* Configure leave policies  
* Configure leave limits  
* Manage departments  
* Manage leave balances  
* Generate reports  
* Access analytics dashboards  
* View audit logs  
* Handle exceptional approval scenarios  
  ---

## **4\. Super Admin**

Super Admins should have access to:

* Full system controls  
* Global settings  
* Role management  
* Permission management  
* Security configurations  
* System monitoring  
* Audit logs  
* Database management utilities  
* Administrative analytics  
  ---

# **Frontend Development Rules**

The frontend must use:

* Next.js App Router or modern React architecture  
* Tailwind CSS  
* React Hook Form  
* Zod validation  
* Axios or Fetch API  
* Context API or Redux Toolkit

Frontend implementation rules:

* All forms must use React Hook Form  
* All validations must use Zod schemas  
* All API calls must be centralized  
* Reusable form components must be created  
* Reusable modal components must be created  
* Reusable dashboard components must be created  
* Reusable table components must be created  
* Reusable button and input components must be created

The frontend must:

* Avoid duplicated code  
* Use reusable layouts  
* Use reusable hooks  
* Prevent unnecessary rerenders  
* Use lazy loading  
* Support loading and suspense states

Protected routes must:

* Validate authentication state  
* Validate user roles  
* Redirect unauthorized users properly

Frontend state management must:

* Separate UI state from server state  
* Prevent stale UI updates  
* Synchronize leave balances correctly  
* Synchronize approval states correctly  
  ---

# **Backend Development Rules**

The backend must follow:

* Service-based architecture  
* Modular route structure  
* Centralized middleware handling  
* Reusable validation middleware  
* Reusable authentication middleware

The backend must implement:

* Controllers  
* Services  
* Repositories or data access layers  
* Middleware layers  
* Utility helpers  
* Shared validation schemas

The backend must never:

* Place business logic directly inside routes  
* Expose sensitive server errors  
* Trust frontend validation alone  
* Allow unvalidated payloads

All APIs must:

* Use standardized JSON responses  
* Use proper HTTP status codes  
* Include centralized error handling  
* Include validation middleware  
* Include authentication middleware

The backend must:

* Use async/await properly  
* Handle promise rejections safely  
* Prevent memory leaks  
* Prevent duplicate processing requests  
* Handle graceful shutdown safely  
  ---

# **Authentication and Authorization Requirements**

The application must implement enterprise-grade authentication and authorization.

Authentication features must include:

* User registration  
* Secure login  
* Secure logout  
* Forgot password  
* Reset password  
* Email verification  
* JWT authentication  
* Refresh token support  
* Session timeout handling  
* Multi-session support if needed

Password rules must include:

* Minimum 8 characters  
* Uppercase letters  
* Lowercase letters  
* Numbers  
* Special characters

Security implementation must include:

* Password hashing using bcrypt  
* Secure JWT handling  
* Protected frontend routes  
* Protected backend APIs  
* Role-based access control  
* Permission validation  
* Session expiration handling  
* Refresh token rotation if implemented

The system must protect against:

* Unauthorized access  
* Token misuse  
* Role escalation  
* Brute-force attacks  
* Session hijacking  
  ---

# **Dashboard Requirements**

## **Employee Dashboard**

The employee dashboard should display:

* Total leave balance  
* Used leave days  
* Remaining leave balance  
* Pending leave requests  
* Approved requests  
* Rejected requests  
* Recent activity  
* Notifications  
* Upcoming holidays  
* Leave history summaries  
  ---

## **Manager Dashboard**

The manager dashboard should display:

* Pending approvals  
* Team leave summaries  
* Department statistics  
* Employee leave reports  
* Approval activities  
* Team availability overview  
  ---

## **Admin Dashboard**

The admin dashboard should display:

* Total employees  
* Active leave requests  
* Pending approvals  
* Monthly leave analytics  
* Department-wise leave trends  
* Approval statistics  
* Administrative alerts  
* System activity summaries  
  ---

# **Leave Request System Requirements**

The system must support:

* Sick Leave  
* Casual Leave  
* Earned Leave  
* Emergency Leave  
* Maternity Leave  
* Paternity Leave  
* Half-Day Leave  
* Unpaid Leave  
* Custom leave types

Employees should be able to:

* Create leave requests  
* Edit pending requests  
* Cancel requests  
* Track approval status  
* View leave history

Managers and admins should be able to:

* Approve requests  
* Reject requests  
* Add comments  
* Review leave history  
* Track approval activities

Admins should also be able to:

* Configure leave policies  
* Configure leave limits  
* Configure leave accrual rules  
* Configure leave carry-forward rules  
  ---

# **Leave Request Form Requirements**

The leave request form must include:

* Employee Name  
* Employee ID  
* Leave Type  
* Start Date  
* End Date  
* Reason for Leave

Optional fields may include:

* Emergency contact  
* Supporting documents  
* Medical certificates  
* Additional notes  
* Attachments

The form must:

* Be responsive  
* Support accessibility  
* Display inline validation errors  
* Prevent invalid submissions  
* Provide user-friendly feedback  
  ---

# **Input Validation Requirements**

All validations must run on both frontend and backend.

The system must validate:

* Names  
* Employee IDs  
* Emails  
* Passwords  
* Phone numbers  
* Leave dates  
* Leave durations  
* Leave reasons  
* File uploads  
* API payloads  
* Query parameters  
* Route parameters

Validation rules must include:

* Empty field prevention  
* Duplicate employee prevention  
* Duplicate leave request prevention  
* Proper email validation  
* Proper phone validation  
* Strong password validation  
* Date range validation  
* Overlapping leave prevention  
* Weekend and holiday validation  
* Minimum and maximum field length validation  
* Safe file upload validation  
* MIME type validation  
* File extension validation  
* File size validation  
* Unsafe content sanitization

The system must:

* Trim unnecessary spaces  
* Prevent XSS attacks  
* Prevent SQL injection  
* Prevent NoSQL injection  
* Prevent duplicate form submissions  
* Prevent invalid status transitions  
* Prevent concurrent approval conflicts  
* Handle race conditions safely

Validation must use:

* Zod or equivalent schema validation libraries  
  ---

# **Approval Workflow Requirements**

The leave approval workflow should follow this sequence:

1. Employee submits leave request  
2. System validates request  
3. Request is stored with pending status  
4. Manager receives notification  
5. Manager reviews request  
6. Manager approves or rejects request  
7. Employee receives notification  
8. Leave balance updates automatically  
9. Audit logs are updated

Workflow rules must:

* Prevent self-approval  
* Prevent duplicate approvals  
* Prevent invalid state transitions  
* Maintain audit history  
* Store timestamps for all actions  
* Store approval and rejection comments  
* Prevent conflicting updates  
* Support future multi-level approvals  
  ---

# **Notification System Requirements**

The system must support:

* Email notifications  
* In-app notifications  
* Real-time updates

Notifications should trigger for:

* Leave submission  
* Leave approval  
* Leave rejection  
* Leave cancellation  
* Leave modification  
* Password reset  
* Account creation  
* Policy updates  
* Security alerts

Notification messages should:

* Be professional  
* Include relevant details  
* Include timestamps where required

The backend should use:

* Nodemailer  
* SMTP services  
* Environment variables

Optional integrations may include:

* SendGrid  
* Mailgun  
* Firebase notifications  
  ---

# **Backend Requirements**

The backend should expose secure REST APIs for:

* Authentication  
* User management  
* Leave requests  
* Approval workflows  
* Notifications  
* Reporting  
* Analytics  
* Audit logs

Backend requirements must include:

* Structured JSON responses  
* Proper HTTP status codes  
* Validation middleware  
* Authentication middleware  
* Authorization middleware  
* Pagination support  
* Filtering support  
* Search support  
* Sorting support  
* Logging and monitoring  
* Rate limiting  
* Request sanitization

The backend must:

* Avoid exposing sensitive data  
* Handle failures gracefully  
* Prevent server crashes  
* Support scalable architecture  
  ---

# **API Engineering Rules**

All APIs must follow RESTful conventions.

API routes should follow structures such as:

* /api/auth  
* /api/users  
* /api/leaves  
* /api/notifications  
* /api/reports

All API responses must follow:

* success  
* message  
* data  
* errors

The backend must implement:

* Global error middleware  
* Request logging middleware  
* Validation middleware  
* Security middleware  
* Rate limiting middleware  
  ---

# **API Response Requirements**

All APIs must return structured JSON responses.

Success responses should include:

* Success status  
* Readable message  
* Relevant response data

Error responses should include:

* Error status  
* Validation details  
* Proper error messages

Example success response:

* {  
*   "success": true,  
*   "message": "Leave request submitted successfully",  
*   "data": {  
*     "requestId": "REQ123",  
*     "status": "Pending"  
*   }  
* }


Example error response:

* {  
*   "success": false,  
*   "message": "Validation failed",  
*   "errors": {  
*     "startDate": "Start date cannot be in the past"  
*   }  
* }  
    
  ---

# **Data Processing Requirements**

Before processing any input, the system must:

* Sanitize user input  
* Trim spaces  
* Validate payloads  
* Prevent unsafe script execution  
* Validate leave balances  
* Validate leave durations  
* Verify permissions  
* Verify request ownership

The system must also:

* Calculate leave durations correctly  
* Track timestamps  
* Store rejection comments  
* Maintain request history  
* Update audit logs automatically  
* Prevent duplicate processing  
  ---

# **Database Requirements**

The application should use:

* MongoDB  
  OR  
* PostgreSQL

The database must store:

* Users  
* Roles  
* Leave requests  
* Leave balances  
* Notifications  
* Leave policies  
* Audit logs  
* System logs  
* Departments  
* Teams

Database requirements must include:

* Proper indexing  
* Optimized queries  
* Relationship management  
* Atomic updates  
* Transactions for sensitive operations  
* createdAt timestamps  
* updatedAt timestamps  
* Soft delete support

The database must:

* Prevent inconsistent leave balances  
* Prevent duplicate writes  
* Support scalable analytics queries  
* Support future scalability  
  ---

# **File Upload Engineering Rules**

File uploads must:

* Validate MIME types  
* Validate extensions  
* Validate file sizes  
* Generate secure filenames

The system must:

* Prevent executable uploads  
* Prevent unsafe scripts  
* Restrict unauthorized file access  
* Store uploads securely

Optional storage integrations may include:

* Cloudinary  
* AWS S3  
* Firebase Storage  
  ---

# **Security Requirements**

The application must protect against:

* XSS attacks  
* CSRF attacks  
* SQL injection  
* NoSQL injection  
* Brute-force attacks  
* Unauthorized API access  
* Unsafe file uploads  
* Rate limit abuse  
* Session hijacking

Security implementation must include:

* Password hashing  
* Secure JWT handling  
* Secure environment variables  
* Secure HTTP headers  
* Input sanitization  
* Rate limiting  
* Role validation  
* Safe error responses

Sensitive information such as:

* Passwords  
* Tokens  
* API keys  
* Database credentials  
* SMTP credentials

must never be exposed publicly.

---

# **Error Handling Requirements**

Frontend error handling must handle:

* Invalid form submissions  
* API failures  
* Session expiration  
* File upload failures  
* Network issues  
* Unauthorized access  
* Slow server responses  
* Empty states

Frontend UI should display:

* Inline validation messages  
* Toast notifications  
* Loading indicators  
* Retry suggestions  
* Friendly error messages

Backend error handling must handle:

* Validation failures  
* Database failures  
* Duplicate entries  
* Email failures  
* Authentication failures  
* Authorization failures  
* File upload failures  
* Timeout errors  
* Unexpected server errors

The backend must:

* Use centralized error middleware  
* Prevent crashes  
* Log failures properly  
* Hide stack traces in production  
* Return structured error responses  
  ---

# **Logging and Monitoring Rules**

The system must maintain logs for:

* Login attempts  
* Leave submissions  
* Leave approvals  
* Leave rejections  
* Password resets  
* Failed API requests  
* Security-related events  
* Administrative activities

The system should support:

* Winston  
* Morgan  
* Sentry

Monitoring must support:

* Production debugging  
* Performance tracking  
* Error monitoring  
* Audit tracking  
  ---

# **Reporting and Analytics Requirements**

The admin system should support:

* Monthly leave reports  
* Department-wise leave trends  
* Employee leave summaries  
* Approval statistics  
* Leave balance reports

Reports should support:

* Filtering  
* Searching  
* Sorting  
* CSV export  
* PDF export  
* Excel export

Analytics should:

* Be visually organized  
* Support large datasets  
* Be easy to understand  
  ---

# **Search, Filter, and Sorting Requirements**

The application should support:

* Employee search  
* Leave request search  
* Department filtering  
* Leave type filtering  
* Status filtering  
* Date range filtering

Sorting should support:

* Newest first  
* Oldest first  
* Pending requests  
* Approved requests  
* Rejected requests

The system should also support:

* Pagination  
* Debounced searching  
* Empty result states  
  ---

# **Performance and Scalability Requirements**

Frontend optimization must include:

* Lazy loading  
* Code splitting  
* Reduced bundle size  
* Optimized rendering  
* Memoization where needed

Backend optimization must include:

* Query optimization  
* Proper indexing  
* Pagination  
* Caching strategies  
* Background jobs for emails

The architecture should support:

* High traffic handling  
* Future scalability  
* Redis caching  
* Queue-based processing  
* Monitoring tools  
  ---

# **Accessibility Requirements**

Accessibility implementation must include:

* Semantic HTML  
* Keyboard navigation  
* ARIA labels  
* Screen reader support  
* Proper contrast ratios  
* Accessible forms  
* Accessible modals  
* Touch-friendly components

The application must remain accessible across all workflows.

---

# **Responsive Design Requirements**

The Leave Management System must support:

* Mobile devices  
* Tablets  
* Laptops  
* Desktop screens

Responsive behavior must include:

* Flexible layouts  
* Responsive tables  
* Adaptive navigation  
* Readable typography  
* Proper spacing  
  ---

# **Technology Stack**

## **Frontend**

Use:

* Next.js or React  
* Tailwind CSS  
* Zod  
* Fetch API  
* Framer Motion where needed  
  ---

## **Backend**

Use:

* Node.js  
* Express.js or Next.js API routes  
* JWT authentication  
* bcrypt  
* Nodemailer  
* dotenv  
  ---

## **Database**

Use:

* MongoDB  
  OR  
* PostgreSQL  
  ---

## **Optional Technologies**

Optional integrations may include:

* Redis  
* Sentry  
* Cloudinary  
* AWS S3  
* Queue systems  
  ---

# **Folder Structure Requirements**

The project should follow a scalable structure as following:

* /app  
* /components  
* /pages  
* /api  
* /controllers  
* /routes  
* /models  
* /services  
* /repositories  
* /middlewares  
* /utils  
* /hooks  
* /styles  
* /uploads  
* /logs

The architecture must remain scalable and maintainable at all the edge cases.

---

# **Environment Variable Requirements**

Environment variables should store:

* Database URLs  
* JWT secrets  
* Refresh token secrets  
* SMTP credentials  
* API keys  
* Cloud storage credentials

Sensitive values must never be hardcoded.

---

# **Deployment Requirements**

The project must support deployment on:

* Vercel  
* Render  
* Railway  
* Netlify  
* AWS if required

Deployment documentation must explain:

* Dependency installation  
* Environment setup  
* Database configuration  
* Production builds  
* Deployment steps  
* Production testing

Production deployment must include:

* HTTPS support  
* Proper CORS configuration  
* Optimized builds  
* Secure environment handling  
  ---

  # 

# **Testing Requirements**

The system should include testing for:

* Authentication  
* Leave workflows  
* Validation rules  
* Role permissions  
* Approval workflows  
* Error handling  
* API responses

Testing should cover:

* Successful workflows  
* Invalid edge cases  
* Security-related failures  
  ---

# **Documentation Requirements**

The project documentation should include:

* Project overview  
* Setup instructions  
* Folder structure explanation  
* API documentation  
* Validation rules  
* Error handling explanation  
* Deployment steps  
* Testing instructions  
* Troubleshooting guidance

Documentation should remain:

* Clear  
* Beginner-friendly  
* Detailed  
* Easy to follow  
  ---

# **AI Code Generation Rules**

Generate:

* Production-quality code  
* Modular architecture  
* Reusable components  
* Reusable APIs  
* Scalable folder structures  
* Clean naming conventions  
* Proper comments where necessary

Do not:

* Use insecure coding practices  
* Hardcode credentials  
* Skip validations  
* Skip authorization checks  
* Skip error handling  
* Generate placeholder logic

The generated project must:

* Be deployment-ready  
* Follow enterprise engineering standards  
* Follow clean code principles  
* Be scalable  
* Be maintainable  
* Be suitable for real-world production usage  
  ---
# **Final Output Requirements**

The final Leave Management System must include:

* Modern frontend UI  
* Secure backend APIs  
* Authentication system  
* Role-based authorization  
* Leave request workflows  
* Approval and rejection management  
* Leave balance tracking  
* Notification system  
* Reporting and analytics  
* Validation handling  
* Error handling  
* Logging and monitoring  
* Security protection  
* Accessibility support  
* Deployment-ready architecture

The final application should be:

* Scalable  
* Secure  
* Maintainable  
* Production-ready  
* Enterprise-grade  
* Suitable for real-world company usage


