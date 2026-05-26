import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import api from "../services/api";
import {
  getRedirectPathByRole,
  REGISTRATION_SESSION_DURATION_MS,
  saveAuthSession,
} from "../services/auth";

function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    department: "",
    role: "employee",
    managerAuthCode: "",
  });
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isDisabled = useMemo(() => {
    return (
      !formData.name.trim() ||
      !formData.email.trim() ||
      !formData.password.trim() ||
      !formData.department.trim() ||
      (formData.role === "manager" && !formData.managerAuthCode.trim()) ||
      isSubmitting
    );
  }, [formData, isSubmitting]);

  const roleCards = [
    {
      role: "employee",
      title: "Employee registration",
      icon: "E",
    },
    {
      role: "manager",
      title: "Manager registration",
      icon: "M",
    },
  ];

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleRoleSelect = (role) => {
    setFormData((current) => ({
      ...current,
      role,
      managerAuthCode: role === "manager" ? current.managerAuthCode : "",
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccessMessage("");
    setIsSubmitting(true);

    try {
      const { data } = await api.post("/auth/register", formData);

      saveAuthSession({
        token: data.token,
        user: data.user,
      }, REGISTRATION_SESSION_DURATION_MS);

      setSuccessMessage(data.message);
      navigate(getRedirectPathByRole(data.user.role));
    } catch (requestError) {
      setError(requestError.response?.data?.message || "Registration failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="page register-page">
      <button type="button" className="back-button" onClick={() => navigate(-1)}>
        <span aria-hidden="true">←</span>
        Back
      </button>

      <div className="auth-shell auth-shell-centered">
        <div className="auth-card">
          <span className="section-label">Get started</span>
          <h1>Create a new account</h1>
          <p>
            Employees can register directly. Managers must enter a valid
            authorization code before their account can be created.
          </p>

          <div className="registration-role-grid">
            {roleCards.map((item) => (
              <button
                key={item.role}
                type="button"
                className={
                  formData.role === item.role
                    ? "registration-role-card registration-role-card-active"
                    : "registration-role-card"
                }
                onClick={() => handleRoleSelect(item.role)}
              >
                <span className="registration-role-icon" aria-hidden="true">
                  {item.icon}
                </span>
                <span className="registration-role-title">{item.title}</span>
              </button>
            ))}
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="register-name">Full name</label>
              <input
                id="register-name"
                name="name"
                type="text"
                placeholder="Khushi"
                value={formData.name}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="register-email">Email</label>
              <input
                id="register-email"
                name="email"
                type="email"
                placeholder="khushi@example.com"
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div className="grid-two">
              <div className="form-group">
                <label htmlFor="register-password">Password</label>
                <input
                  id="register-password"
                  name="password"
                  type="password"
                  placeholder="Choose a password"
                  value={formData.password}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label htmlFor="register-department">Department</label>
                <input
                  id="register-department"
                  name="department"
                  type="text"
                  placeholder="IT"
                  value={formData.department}
                  onChange={handleChange}
                />
              </div>
            </div>

            {formData.role === "manager" ? (
              <div className="form-group">
                <label htmlFor="register-manager-code">Manager authorization code</label>
                <input
                  id="register-manager-code"
                  name="managerAuthCode"
                  type="password"
                  placeholder="Enter manager authorization code"
                  value={formData.managerAuthCode}
                  onChange={handleChange}
                />
              </div>
            ) : null}

            {error ? <p className="form-message form-error">{error}</p> : null}
            {successMessage ? <p className="form-message form-success">{successMessage}</p> : null}

            <button type="submit" className="button-primary" disabled={isDisabled}>
              {isSubmitting ? "Creating account..." : "Register"}
            </button>
          </form>

          <div className="link-row">
            <span className="auth-helper">Already registered?</span>
            <Link className="inline-link" to="/login">
              Go to login
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Register;
