import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import { clearAuthSession } from "../services/auth";

function ApplyLeave() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    leaveType: "casual",
    startDate: "",
    endDate: "",
    reason: "",
  });
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const requestedDays = useMemo(() => {
    if (!formData.startDate || !formData.endDate) {
      return "";
    }

    const start = new Date(formData.startDate);
    const end = new Date(formData.endDate);
    const diff = Math.floor((end - start) / (1000 * 60 * 60 * 24)) + 1;

    if (Number.isNaN(diff) || diff <= 0) {
      return "Invalid range";
    }

    return `${diff} day${diff > 1 ? "s" : ""}`;
  }, [formData.endDate, formData.startDate]);

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
    setSuccessMessage("");
    setIsSubmitting(true);

    try {
      const { data } = await api.post("/leaves/apply", formData);
      setSuccessMessage(data.message);
      setFormData({
        leaveType: "casual",
        startDate: "",
        endDate: "",
        reason: "",
      });

      window.setTimeout(() => {
        navigate("/employee/leave-history");
      }, 800);
    } catch (requestError) {
      setError(requestError.response?.data?.message || "Could not submit leave request");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="page">
      <div className="page-actions">
        <button type="button" className="back-button" onClick={() => navigate(-1)}>
          <span aria-hidden="true">&larr;</span>
          Back
        </button>
        <button
          type="button"
          className="back-button logout-button"
          onClick={() => {
            clearAuthSession();
            navigate("/login", { replace: true });
          }}
        >
          Logout
        </button>
      </div>

      <div className="page-header">
        <div>
          <span className="section-label">Leave request form</span>
          <h1>Submit a new leave request.</h1>
        </div>
      </div>

      <div className="panel">
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="grid-two">
            <div className="form-group">
              <label htmlFor="leave-type">Leave type</label>
              <select
                id="leave-type"
                name="leaveType"
                value={formData.leaveType}
                onChange={handleChange}
              >
                <option value="casual">Casual</option>
                <option value="sick">Sick</option>
                <option value="earned">Earned</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="leave-start">Start date</label>
              <input
                id="leave-start"
                name="startDate"
                type="date"
                value={formData.startDate}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="grid-two">
            <div className="form-group">
              <label htmlFor="leave-end">End date</label>
              <input
                id="leave-end"
                name="endDate"
                type="date"
                value={formData.endDate}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="leave-days">Requested days</label>
              <input
                id="leave-days"
                type="text"
                placeholder="Calculated later"
                value={requestedDays}
                disabled
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="leave-reason">Reason</label>
            <textarea
              id="leave-reason"
              name="reason"
              placeholder="Share the context for your leave request"
              value={formData.reason}
              onChange={handleChange}
            />
          </div>

          {error ? <p className="form-message form-error">{error}</p> : null}
          {successMessage ? <p className="form-message form-success">{successMessage}</p> : null}

          <button type="submit" className="button-primary" disabled={isSubmitting}>
            {isSubmitting ? "Submitting..." : "Submit leave request"}
          </button>
        </form>
      </div>
    </section>
  );
}

export default ApplyLeave;
