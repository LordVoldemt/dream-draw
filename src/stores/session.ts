import { defineStore } from "pinia";

export type SessionRole = "guest" | "user" | "admin";

interface SessionState {
  userToken: string | null;
  adminToken: string | null;
  pointsBalance: number | null;
  phone: string | null;
}

export const useSessionStore = defineStore("session", {
  state: (): SessionState => ({
    userToken: null,
    adminToken: null,
    pointsBalance: null,
    phone: null,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.userToken),
    isAdminAuthenticated: (state) => Boolean(state.adminToken),
    role: (state): SessionRole => {
      if (state.adminToken) {
        return "admin";
      }
      if (state.userToken) {
        return "user";
      }
      return "guest";
    },
  },
  actions: {
    setUserToken(token: string | null) {
      this.userToken = token;
    },
    setAdminToken(token: string | null) {
      this.adminToken = token;
    },
    setUserProfile(payload: { phone: string; pointsBalance: number }) {
      this.phone = payload.phone;
      this.pointsBalance = payload.pointsBalance;
    },
    setPointsBalance(points: number) {
      this.pointsBalance = points;
    },
    reset() {
      this.userToken = null;
      this.adminToken = null;
      this.pointsBalance = null;
      this.phone = null;
    },
  },
});
