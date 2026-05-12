import { createRouter, createWebHistory } from "vue-router";

import AdminPanel from "../views/AdminPanel.vue";
import ForgotPasswordView from "../views/ForgotPasswordView.vue";
import GraphExplore from "../views/GraphExploreForum.vue";
import Home from "../views/Home.vue";
import LoginView from "../views/LoginView.vue";
import PersonalCenter from "../views/PersonalCenter.vue";
import RegisterView from "../views/RegisterView.vue";
import SearchResult from "../views/SearchResult.vue";
import TeacherDashboard from "../views/TeacherDashboardForum.vue";
import { getCurrentUser } from "../utils/session";
import { getDefaultRouteByRole, hasRouteAccess } from "../utils/role";

const routes = [
  { path: "/", name: "home", component: Home },
  { path: "/login", name: "login", component: LoginView, meta: { guestOnly: true } },
  { path: "/register", name: "register", component: RegisterView, meta: { guestOnly: true } },
  { path: "/forgot-password", name: "forgot-password", component: ForgotPasswordView, meta: { guestOnly: true } },
  { path: "/graph", name: "graph", component: GraphExplore },
  { path: "/search", name: "search", component: SearchResult },
  { path: "/personal", name: "personal", component: PersonalCenter, meta: { requiresAuth: true } },
  { path: "/teacher", name: "teacher", component: TeacherDashboard, meta: { requiresAuth: true, roles: ["teacher"] } },
  { path: "/admin", name: "admin", component: AdminPanel, meta: { requiresAuth: true, roles: ["admin"] } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const user = getCurrentUser();
  if (to.meta?.guestOnly && user) {
    return getDefaultRouteByRole(user.role);
  }
  if (to.meta?.requiresAuth && !user) {
    return "/login";
  }
  if (!hasRouteAccess(user, to.meta?.roles || [])) {
    return user ? getDefaultRouteByRole(user.role) : "/login";
  }
  return true;
});

export default router;
