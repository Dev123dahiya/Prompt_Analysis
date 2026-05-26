import { useEffect } from "react";
import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";

import Navbar from "./components/Navbar";
import ApplyLeave from "./pages/ApplyLeave";
import EmployeeDashboard from "./pages/EmployeeDashboard";
import LeaveHistory from "./pages/LeaveHistory";
import Login from "./pages/Login";
import ManagerDashboard from "./pages/ManagerDashboard";
import Register from "./pages/Register";
import { clearAuthSession, getAuthSession, getSessionTimeRemaining } from "./services/auth";
import "./App.css";

function SessionWatcher() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const remaining = getSessionTimeRemaining();

    if (!remaining) {
      return undefined;
    }

    const timeoutId = window.setTimeout(() => {
      clearAuthSession();
      navigate("/", { replace: true, state: { sessionExpired: true } });
    }, remaining);

    return () => window.clearTimeout(timeoutId);
  }, [location.pathname, navigate]);

  return null;
}

function PublicOnlyRoute({ children }) {
  const session = getAuthSession();

  if (session?.token && session?.user) {
    return <Navigate to={session.user.role === "manager" ? "/manager/dashboard" : "/employee/dashboard"} replace />;
  }

  return children;
}

function ProtectedRoute({ allowedRoles, children }) {
  const session = getAuthSession();

  if (!session?.token || !session?.user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(session.user.role)) {
    return <Navigate to="/" replace />;
  }

  return children;
}

function App() {
  return (
    <div className="app-shell">
      <SessionWatcher />
      <Navbar />
      <main className="app-main">
        <Routes>
          <Route
            path="/"
            element={
              <PublicOnlyRoute>
                <Login />
              </PublicOnlyRoute>
            }
          />
          <Route
            path="/login"
            element={
              <PublicOnlyRoute>
                <Login />
              </PublicOnlyRoute>
            }
          />
          <Route
            path="/register"
            element={
              <PublicOnlyRoute>
                <Register />
              </PublicOnlyRoute>
            }
          />
          <Route
            path="/employee/dashboard"
            element={
              <ProtectedRoute allowedRoles={["employee"]}>
                <EmployeeDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/employee/apply-leave"
            element={
              <ProtectedRoute allowedRoles={["employee"]}>
                <ApplyLeave />
              </ProtectedRoute>
            }
          />
          <Route
            path="/employee/leave-history"
            element={
              <ProtectedRoute allowedRoles={["employee"]}>
                <LeaveHistory />
              </ProtectedRoute>
            }
          />
          <Route
            path="/manager/dashboard"
            element={
              <ProtectedRoute allowedRoles={["manager"]}>
                <ManagerDashboard />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
