import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it } from "vitest";
import { createAppRouter } from "@/router";
import { useSessionStore } from "@/stores/session";

describe("router guards", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("allows public home route", async () => {
    const router = createAppRouter(true);
    await router.push("/");
    await router.isReady();

    expect(router.currentRoute.value.name).toBe("home");
  });

  it("allows unauthenticated users to enter workspace before submit", async () => {
    const router = createAppRouter(true);
    await router.push("/workspace");
    await router.isReady();

    expect(router.currentRoute.value.name).toBe("workspace");
  });

  it("redirects unauthenticated admins to admin login", async () => {
    const router = createAppRouter(true);
    await router.push("/admin/users");
    await router.isReady();

    expect(router.currentRoute.value.name).toBe("admin-login");
    expect(router.currentRoute.value.query.redirect).toBe("/admin/users");
  });

  it("keeps authenticated user on protected user route", async () => {
    const session = useSessionStore();
    session.setUserToken("user-token");

    const router = createAppRouter(true);
    await router.push("/workspace");
    await router.isReady();

    expect(router.currentRoute.value.name).toBe("workspace");
  });

  it("keeps authenticated admin on protected admin route", async () => {
    const session = useSessionStore();
    session.setAdminToken("admin-token");

    const router = createAppRouter(true);
    await router.push("/admin/model-monitoring");
    await router.isReady();

    expect(router.currentRoute.value.name).toBe("admin-model-monitoring");
  });
});
