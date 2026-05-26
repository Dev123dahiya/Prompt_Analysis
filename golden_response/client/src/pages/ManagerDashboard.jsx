import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import { clearAuthSession } from "../services/auth";
import { formatDateRange } from "../utils/leave";

function ManagerDashboard() {
  const navigate = useNavigate();
  const [pendingRequests, setPendingRequests] = useState([]);
  const [selectedLeaveId, setSelectedLeaveId] = useState("");
  const [managerRemark, setManagerRemark] = useState("");
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);

  const selectedRequest = useMemo(
    () => pendingRequests.find((request) => request._id === selectedLeaveId) || null,
    [pendingRequests, selectedLeaveId]
  );

  useEffect(() => {
    const loadPendingRequests = async () => {
      try {
        const { data } = await api.get("/leaves/pending");
        setPendingRequests(data.leaves || []);
        setError("");
      } catch (requestError) {
        setError(requestError.response?.data?.message || "Could not load pending requests");
      } finally {
        setIsLoading(false);
      }
    };

    loadPendingRequests();
  }, []);

  const handleDecision = async (status) => {
    if (!selectedLeaveId) {
      setError("Select a leave request before taking action.");
      return;
    }

    setError("");
    setSuccessMessage("");
    setIsUpdating(true);

    try {
      const { data } = await api.put(`/leaves/${selectedLeaveId}/status`, {
        status,
        managerRemark,
      });

      setPendingRequests((current) =>
        current.filter((request) => request._id !== selectedLeaveId)
      );
      setSelectedLeaveId("");
      setManagerRemark("");
      setSuccessMessage(data.message);
    } catch (requestError) {
      setError(requestError.response?.data?.message || "Could not update leave status");
    } finally {
      setIsUpdating(false);
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
          <span className="section-label">Manager dashboard</span>
          <h1>Review requests and keep approvals moving.</h1>
        </div>
      </div>

      {error ? <p className="form-message form-error">{error}</p> : null}
      {successMessage ? <p className="form-message form-success">{successMessage}</p> : null}

      <div className="dashboard-grid">
        <section className="dashboard-card table-card">
          <div className="page-header">
            <div>
              <span className="section-label">Pending approvals</span>
              <h2>Requests waiting for review</h2>
            </div>
          </div>

          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Employee</th>
                  <th>Leave type</th>
                  <th>Dates</th>
                  <th>Department</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr>
                    <td colSpan="5" className="empty-state">
                      Loading pending requests...
                    </td>
                  </tr>
                ) : pendingRequests.length ? (
                  pendingRequests.map((request) => (
                    <tr
                      key={request._id}
                      className={selectedLeaveId === request._id ? "table-row-active" : ""}
                    >
                      <td>{request.user?.name || "-"}</td>
                      <td>{request.leaveType} leave</td>
                      <td>{formatDateRange(request.startDate, request.endDate)}</td>
                      <td>{request.user?.department || "-"}</td>
                      <td>
                        <button
                          type="button"
                          className="button-secondary table-action"
                          onClick={() => {
                            setSelectedLeaveId(request._id);
                            setSuccessMessage("");
                          }}
                        >
                          {selectedLeaveId === request._id ? "Selected" : "Review"}
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="empty-state">
                      No pending leave requests right now.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <aside className="activity-card">
          <span className="section-label">Decision panel</span>
          <h3>{selectedRequest ? `Reviewing ${selectedRequest.user?.name}'s request` : "Select a request to continue"}</h3>

          {selectedRequest ? (
            <>
              <ul className="list">
                <li>
                  <div>
                    <strong>Leave type</strong>
                    <p>{selectedRequest.leaveType} leave</p>
                  </div>
                </li>
                <li>
                  <div>
                    <strong>Dates</strong>
                    <p>{formatDateRange(selectedRequest.startDate, selectedRequest.endDate)}</p>
                  </div>
                </li>
                <li>
                  <div>
                    <strong>Reason</strong>
                    <p>{selectedRequest.reason}</p>
                  </div>
                </li>
              </ul>

              <div className="form-group">
                <label htmlFor="manager-remark">Manager remark</label>
                <textarea
                  id="manager-remark"
                  value={managerRemark}
                  onChange={(event) => setManagerRemark(event.target.value)}
                  placeholder="Add an optional note for the employee"
                />
              </div>

              <div className="decision-actions">
                <button
                  type="button"
                  className="button-primary"
                  disabled={isUpdating}
                  onClick={() => handleDecision("Approved")}
                >
                  {isUpdating ? "Saving..." : "Approve"}
                </button>
                <button
                  type="button"
                  className="button-secondary"
                  disabled={isUpdating}
                  onClick={() => handleDecision("Rejected")}
                >
                  Reject
                </button>
              </div>
            </>
          ) : (
            <p className="empty-state">
              Pick a pending request from the table to approve or reject it.
            </p>
          )}
        </aside>
      </div>
    </section>
  );
}

export default ManagerDashboard;
