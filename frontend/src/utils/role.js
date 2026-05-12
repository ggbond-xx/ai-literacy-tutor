export const roleTextMap = {
  student: "学生",
  teacher: "教师",
  admin: "图谱运维官",
};

export function getDefaultRouteByRole(role) {
  if (role === "teacher") {
    return "/teacher";
  }
  if (role === "admin") {
    return "/admin";
  }
  return "/graph";
}

export function hasRouteAccess(user, allowedRoles = []) {
  if (!allowedRoles.length) {
    return true;
  }
  if (!user) {
    return false;
  }
  return allowedRoles.includes(user.role);
}
