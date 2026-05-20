import { createRouter, createMemoryHistory, createWebHistory } from "vue-router";
import UserLayout from "@/layouts/UserLayout.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { requireAdminAuth, requireUserAuth } from "./guards";

export const routes = [
  {
    path: "/",
    component: UserLayout,
    children: [
      {
        path: "",
        name: "home",
        component: () => import("@/views/user/HomeView.vue"),
      },
      {
        path: "workspace",
        name: "workspace",
        component: () => import("@/views/user/GenerateView.vue"),
      },
      {
        path: "works",
        name: "works",
        component: () => import("@/views/user/WorksView.vue"),
        beforeEnter: requireUserAuth,
      },
      {
        path: "reward",
        name: "reward",
        component: () => import("@/views/user/FirstLoginRewardView.vue"),
        beforeEnter: requireUserAuth,
      },
      {
        path: "generating",
        name: "generating",
        component: () => import("@/views/user/GeneratingView.vue"),
        beforeEnter: requireUserAuth,
      },
      {
        path: "result/:id",
        name: "result",
        component: () => import("@/views/user/ResultView.vue"),
        beforeEnter: requireUserAuth,
      },
      {
        path: "pricing",
        name: "pricing",
        component: () => import("@/views/user/PricingView.vue"),
        beforeEnter: requireUserAuth,
      },
      {
        path: "login",
        name: "login",
        component: () => import("@/views/user/LoginView.vue"),
      },
      {
        path: "register",
        name: "register",
        component: () => import("@/views/user/RegisterView.vue"),
      },
    ],
  },
  {
    path: "/admin",
    component: AdminLayout,
    children: [
      {
        path: "login",
        name: "admin-login",
        component: () => import("@/views/admin/AdminLoginView.vue"),
      },
      {
        path: "",
        name: "admin-dashboard",
        component: () => import("@/views/admin/AdminDashboardView.vue"),
        beforeEnter: requireAdminAuth,
      },
      {
        path: "users",
        name: "admin-users",
        component: () => import("@/views/admin/UserManagementView.vue"),
        beforeEnter: requireAdminAuth,
      },
      {
        path: "users/:id",
        name: "admin-user-detail",
        component: () => import("@/views/admin/UserDetailView.vue"),
        beforeEnter: requireAdminAuth,
      },
      {
        path: "model-providers",
        name: "admin-model-providers",
        component: () => import("@/views/admin/ModelProvidersView.vue"),
        beforeEnter: requireAdminAuth,
      },
      {
        path: "model-monitoring",
        name: "admin-model-monitoring",
        component: () => import("@/views/admin/ModelMonitoringView.vue"),
        beforeEnter: requireAdminAuth,
      },
    ],
  },
];

export function createAppRouter(memory = false) {
  return createRouter({
    history: memory ? createMemoryHistory() : createWebHistory(),
    routes,
  });
}

export const router = createAppRouter();
