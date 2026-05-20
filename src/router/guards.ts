import type { NavigationGuardNext, RouteLocationNormalized } from "vue-router";
import { useSessionStore } from "@/stores/session";

export function requireUserAuth(
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext,
) {
  const session = useSessionStore();
  if (session.isAuthenticated) {
    next();
    return;
  }
  next({
    name: "login",
    query: { redirect: to.fullPath },
  });
}

export function requireAdminAuth(
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext,
) {
  const session = useSessionStore();
  if (session.isAdminAuthenticated) {
    next();
    return;
  }
  next({
    name: "admin-login",
    query: { redirect: to.fullPath },
  });
}
