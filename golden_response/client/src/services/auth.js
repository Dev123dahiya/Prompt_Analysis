const AUTH_STORAGE_KEY = "leave-management-auth";
const DEFAULT_SESSION_DURATION_MS = 8 * 60 * 60 * 1000;

export const REGISTRATION_SESSION_DURATION_MS = 2 * 60 * 1000;

export const saveAuthSession = (payload, durationMs = DEFAULT_SESSION_DURATION_MS) => {
  const expiresAt = payload.expiresAt || Date.now() + durationMs;

  localStorage.setItem(
    AUTH_STORAGE_KEY,
    JSON.stringify({
      ...payload,
      expiresAt,
    })
  );
};

export const getAuthSession = () => {
  const saved = localStorage.getItem(AUTH_STORAGE_KEY);

  if (!saved) {
    return null;
  }

  try {
    const session = JSON.parse(saved);

    if (session?.expiresAt && session.expiresAt <= Date.now()) {
      localStorage.removeItem(AUTH_STORAGE_KEY);
      return null;
    }

    return session;
  } catch {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    return null;
  }
};

export const clearAuthSession = () => {
  localStorage.removeItem(AUTH_STORAGE_KEY);
};

export const getRedirectPathByRole = (role) => {
  if (role === "manager") {
    return "/manager/dashboard";
  }

  return "/employee/dashboard";
};

export const getSessionTimeRemaining = () => {
  const session = getAuthSession();

  if (!session?.expiresAt) {
    return null;
  }

  return Math.max(session.expiresAt - Date.now(), 0);
};
