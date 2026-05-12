import http from "./http";

export function fetchAdminOverview() {
  return http.get("/admin/overview");
}

export function createManagedUser(payload) {
  return http.post("/admin/users", payload);
}

export function updateManagedUser(userId, payload) {
  return http.put(`/admin/users/${userId}`, payload);
}

export function deleteManagedUser(userId) {
  return http.delete(`/admin/users/${userId}`);
}

export function deleteManagedQuestion(questionId) {
  return http.delete(`/admin/questions/${questionId}`);
}

export function deleteManagedComment(commentId) {
  return http.delete(`/admin/comments/${commentId}`);
}

export function updateCoordinationRequest(requestId, payload) {
  return http.put(`/admin/coordination/${requestId}`, payload);
}

export function reviewGraphChangeRequest(requestId, payload) {
  return http.put(`/admin/graph-change-requests/${requestId}/review`, payload);
}

export function updateRecommendationSettings(payload) {
  return http.put("/admin/settings/recommendation", payload);
}
