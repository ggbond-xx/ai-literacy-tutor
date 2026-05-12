import http from "./http";

export function registerUser(payload) {
  return http.post("/auth/register", payload);
}

export function loginUser(payload) {
  return http.post("/auth/login", payload);
}

export function fetchCurrentUser() {
  return http.get("/auth/me");
}

export function updateCurrentUserProfile(payload) {
  return http.put("/auth/me/profile", payload);
}
