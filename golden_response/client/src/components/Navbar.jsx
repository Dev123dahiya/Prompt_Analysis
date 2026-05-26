import { NavLink } from "react-router-dom";

import LeavifyLogo from "./LeavifyLogo";
import { clearAuthSession, getAuthSession, getRedirectPathByRole } from "../services/auth";

const navItems = [
  { to: "/login", label: "Login" },
  { to: "/register", label: "Register" },
  { to: "/employee/dashboard", label: "Employee" },
  { to: "/manager/dashboard", label: "Manager" },
];

function Navbar() {
  const session = getAuthSession();
  const dashboardPath = session?.user?.role ? getRedirectPathByRole(session.user.role) : null;
  const visibleNavItems = navItems.filter((item) => {
    if (session?.token && (item.to === "/login" || item.to === "/register")) {
      return false;
    }

    return true;
  });

  return (
    <header className="topbar">
      <div className="topbar-inner">
        <NavLink className="brand" to="/">
          <LeavifyLogo compact />
        </NavLink>

        <nav className="nav-links" aria-label="Primary navigation">
          {dashboardPath ? (
            <NavLink
              to={dashboardPath}
              className={({ isActive }) =>
                isActive ? "nav-link nav-link-active" : "nav-link"
              }
            >
              Dashboard
            </NavLink>
          ) : null}

          {visibleNavItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                isActive ? "nav-link nav-link-active" : "nav-link"
              }
            >
              {item.label}
            </NavLink>
          ))}

          {session?.token ? (
            <button
              type="button"
              className="nav-link nav-button"
              onClick={() => {
                clearAuthSession();
                window.location.href = "/login";
              }}
            >
              Logout
            </button>
          ) : null}
        </nav>
      </div>
    </header>
  );
}

export default Navbar;
