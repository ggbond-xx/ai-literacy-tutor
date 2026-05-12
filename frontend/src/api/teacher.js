import http from "./http";

export function fetchTeacherOverview() {
  return http.get("/teacher/overview");
}

export function replyTeacherQuestion(questionId, teacherReply) {
  return http.put(`/teacher/questions/${questionId}/reply`, { teacher_reply: teacherReply });
}

export function featureTeacherQuestion(questionId, featured) {
  return http.put(`/teacher/questions/${questionId}/feature`, { featured });
}

export function fetchStudentSnapshot(studentId) {
  return http.get(`/teacher/students/${studentId}/snapshot`);
}

export function fetchTeacherConceptAnalytics(conceptId) {
  return http.get(`/teacher/concepts/${encodeURIComponent(conceptId)}/analytics`);
}

export function featureTeacherComment(commentId, isExcellent) {
  return http.put(`/teacher/comments/${commentId}/feature`, { is_excellent: isExcellent });
}

export function createTeacherCoordinationRequest(payload) {
  return http.post("/teacher/coordination", payload);
}

export function createGraphChangeRequest(payload) {
  return http.post("/teacher/graph-change-requests", payload);
}

export function createQuickReplyTemplate(payload) {
  return http.post("/teacher/templates", payload);
}

export function deleteQuickReplyTemplate(templateId) {
  return http.delete(`/teacher/templates/${templateId}`);
}

export function exportTeacherQuestionsCsv() {
  return http.get("/teacher/export/questions", { responseType: "blob" });
}
