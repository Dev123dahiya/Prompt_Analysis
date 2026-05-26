import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import LeavifyLogo from "../components/LeavifyLogo";
import api from "../services/api";
import { getRedirectPathByRole, saveAuthSession } from "../services/auth";

function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isDisabled = useMemo(
    () => !formData.email.trim() || !formData.password.trim() || isSubmitting,
    [formData.email, formData.password, isSubmitting]
  );

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const { data } = await api.post("/auth/login", formData);

      saveAuthSession({
        token: data.token,
        user: data.user,
      });

      navigate(getRedirectPathByRole(data.user.role));
    } catch (requestError) {
      setError(requestError.response?.data?.message || "Login failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="page">
      <button type="button" className="back-button" onClick={() => navigate(-1)}>
        <span aria-hidden="true">←</span>
        Back
      </button>

      <div className="login-layout">
        <aside className="login-showcase">
          <div className="login-brand-block">
            <LeavifyLogo />
            <p className="login-brand-copy">
              Sign in to access the Leavify Leave Management System for employee
              requests and manager approvals.
            </p>
          </div>
        </aside>

        <div className="login-panel">
          <div className="auth-card login-panel-card">
            <span className="section-label">Login Portal</span>
            <h1>Sign in</h1>

            <form className="auth-form" onSubmit={handleSubmit}>
              <div className="login-input-row">
                <span className="login-input-icon" aria-hidden="true">
                  @
                </span>
                <input
                  id="login-email"
                  name="email"
                  type="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>

              <div className="login-input-row">
                <span className="login-input-icon" aria-hidden="true">
                  *
                </span>
                <input
                  id="login-password"
                  name="password"
                  type="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleChange}
                />
              </div>

              {error ? <p className="form-message form-error">{error}</p> : null}

              <button type="submit" className="button-primary login-submit" disabled={isDisabled}>
                {isSubmitting ? "Logging in..." : "LOGIN"}
              </button>
            </form>

            <div className="link-row login-links">
              <Link className="inline-link" to="/register">
                New registration
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Login;
