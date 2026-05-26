import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import api from "../services/api";
import { clearAuthSession, getAuthSession, saveAuthSession } from "../services/auth";
import { formatDateRange } from "../utils/leave";

function EmployeeDashboard() {
  const navigate = useNavigate();
  const session = getAuthSession();
  const [profile, setProfile] = useState(session?.user || null);
  const [leaves, setLeaves] = useState([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [{ data: profileData }, { data: leaveData }] = await Promise.all([
          api.get("/auth/profile"),
          api.get("/leaves/my-leaves"),
        ]);

        setProfile(profileData.user);
        setLeaves(leaveData.leaves || []);
        setError("");

        if (session?.token) {
          saveAuthSession({
            token: session.token,
            user: profileData.user,
          });
        }
      } catch (requestError) {
        setError(requestError.response?.data?.message || "Failed to load dashboard");
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboard();
  }, [session?.token]);

  const summaryItems = [
    { label: "Department", value: profile?.department || "-" },
    {
      label: "Pending requests",
      value: String(leaves.filter((leave) => leave.status === "Pending").length),
    },
    {
      label: "Approved requests",
      value: String(leaves.filter((leave) => leave.status === "Approved").length),
    },
  ];

  const recentRequests = leaves.slice(0, 3);

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
          <span className="section-label">Employee dashboard</span>
          <h1>
            {profile?.name ? `Welcome back, ${profile.name}.` : "Track requests, balances, and recent decisions."}
          </h1>
        </div>
      </div>

      <div className="summary-grid">
        {summaryItems.map((item) => (
          <article key={item.label} className="summary-card">
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </article>
        ))}
      </div>

      <div className="section-stack">
        {error ? <p className="form-message form-error">{error}</p> : null}

        <div className="dashboard-grid">
          <section className="dashboard-card">
            <div className="page-header">
              <div>
                <span className="section-label">Quick actions</span>
                <h2>What employees do most often</h2>
              </div>
            </div>

            <div className="card-grid">
              <article className="feature-card">
                <h3>Apply for leave</h3>
                <p>Start a new leave request with dates, type, and reason.</p>
                <Link className="inline-link" to="/employee/apply-leave">
                  Open form
                </Link>
              </article>
              <article className="feature-card">
                <h3>View history</h3>
                <p>Review status changes and manager remarks in one place.</p>
                <Link className="inline-link" to="/employee/leave-history">
                  See history
                </Link>
              </article>
              <article className="feature-card profile-card">
                <h3>Profile snapshot</h3>
                <p className="profile-card-email">
                  {profile?.email || "Load the protected profile to display employee information here."}
                </p>
                <span className="auth-helper profile-card-role">
                  {profile?.role ? `Role: ${profile.role}` : "Connect to `/api/auth/profile`"}
                </span>
              </article>
            </div>
          </section>

          <aside className="activity-card">
            <span className="section-label">Recent leave requests</span>
            <h3>Latest activity</h3>
            {isLoading ? (
              <p className="auth-helper">Loading your recent requests...</p>
            ) : recentRequests.length ? (
              <ul className="list">
                {recentRequests.map((request) => (
                  <li key={request._id}>
                    <div>
                      <strong>{request.leaveType} leave</strong>
                      <p>{formatDateRange(request.startDate, request.endDate)}</p>
                    </div>
                    <span className={`badge ${request.status.toLowerCase()}`}>
                      {request.status}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="empty-state">No leave requests yet. Apply for your first leave.</p>
            )}
          </aside>
        </div>
      </div>
    </section>
  );
}

export default EmployeeDashboard;
