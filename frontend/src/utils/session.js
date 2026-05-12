const ACCESS_TOKEN_KEY = "access_token";
const CURRENT_USER_KEY = "current_user";

function emitSessionUpdated() {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("session-updated"));
  }
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getCurrentUser() {
  const raw = localStorage.getItem(CURRENT_USER_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function saveSession(accessToken, user) {
  if (accessToken) {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  }
  if (user) {
    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
  }
  emitSessionUpdated();
}

export function clearSession() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(CURRENT_USER_KEY);
  emitSessionUpdated();
}
