import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import { clearAuthSession } from "../services/auth";
import { formatDateRange } from "../utils/leave";

function LeaveHistory() {
  const navigate = useNavigate();
  const [leaveRows, setLeaveRows] = useState([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadLeaves = async () => {
      try {
        const { data } = await api.get("/leaves/my-leaves");
        setLeaveRows(data.leaves || []);
        setError("");
      } catch (requestError) {
        setError(requestError.response?.data?.message || "Could not load leave history");
      } finally {
        setIsLoading(false);
      }
    };

    loadLeaves();
  }, []);

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
          <h1 className="page-title-large">Leave history</h1>
        </div>
      </div>

      {error ? <p className="form-message form-error">{error}</p> : null}

      <section className="dashboard-card table-card">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Leave type</th>
                <th>Dates</th>
                <th>Status</th>
                <th>Manager remark</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan="4" className="empty-state">
                    Loading leave history...
                  </td>
                </tr>
              ) : leaveRows.length ? (
                leaveRows.map((row) => (
                  <tr key={row._id}>
                    <td>{row.leaveType} leave</td>
                    <td>{formatDateRange(row.startDate, row.endDate)}</td>
                    <td>
                      <span className={`badge ${row.status.toLowerCase()}`}>{row.status}</span>
                    </td>
                    <td>{row.managerRemark || "No remark yet"}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="empty-state">
                    No leave requests found yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}

export default LeaveHistory;
