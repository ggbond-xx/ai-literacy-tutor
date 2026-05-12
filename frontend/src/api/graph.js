import http from "./http";

export function fetchGraphAll() {
  return http.get("/graph/all");
}
