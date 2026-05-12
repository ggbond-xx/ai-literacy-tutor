import http from "./http";

export function fetchNotifications() {
  return http.get("/notifications");
}

export function markNotificationRead(notificationId) {
  return http.put(`/notifications/${notificationId}/read`);
}

export function markAllNotificationsRead() {
  return http.put("/notifications/read-all");
}
