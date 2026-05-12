import http from "./http";

export function fetchLearningStatuses() {
  return http.get("/learning/status");
}

export function updateLearningStatus(conceptId, status) {
  return http.put(`/learning/status/${conceptId}`, { status });
}

export function fetchMyQuestions() {
  return http.get("/learning/questions");
}

export function fetchLearningQuestions(params = {}) {
  return http.get("/learning/questions", { params });
}

export function createQuestion(payload) {
  return http.post("/learning/questions", payload);
}

export function toggleQuestionFavorite(questionId) {
  return http.post(`/learning/questions/${questionId}/favorite`);
}

export function createQuestionComment(questionId, content, parentCommentId = null) {
  return http.post(`/learning/questions/${questionId}/comments`, {
    content,
    parent_comment_id: parentCommentId,
  });
}

export function deleteQuestionComment(commentId) {
  return http.delete(`/learning/comments/${commentId}`);
}

export function toggleQuestionCommentLike(commentId) {
  return http.post(`/learning/comments/${commentId}/like`);
}

export function submitQuizAttempt(conceptId, payload) {
  return http.post(`/learning/quiz/${conceptId}/attempts`, payload);
}

export function recordNodeVisit(conceptId, payload = {}) {
  return http.post(`/learning/node-visits/${conceptId}`, payload);
}

export function fetchLearningAnalytics() {
  return http.get("/learning/analytics");
}

export function exportLearningRecordsCsv() {
  return http.get("/learning/export/csv", { responseType: "blob" });
}
