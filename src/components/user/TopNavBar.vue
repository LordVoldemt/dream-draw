<template>
  <header class="top-nav">
    <RouterLink class="brand" to="/">绘梦</RouterLink>
    <nav class="links">
      <RouterLink to="/">首页</RouterLink>
      <RouterLink to="/pricing">画廊</RouterLink>
      <RouterLink to="/workspace">创作空间</RouterLink>
      <RouterLink to="/works">我的作品</RouterLink>
    </nav>
    <div class="actions">
      <span v-if="session.isAuthenticated" class="points">{{ pointsLabel }}</span>
      <RouterLink v-if="!session.isAuthenticated" class="primary" to="/login">手机号登录</RouterLink>
      <button v-else class="primary" type="button" @click="logout">退出登录</button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { useSessionStore } from "@/stores/session";

const session = useSessionStore();
const router = useRouter();

const pointsLabel = computed(() => `${session.pointsBalance ?? 0} 积分`);

function logout() {
  session.reset();
  router.push("/");
}
</script>

<style scoped>
.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 16px 0;
  border-bottom: 1px solid rgba(17, 17, 17, 0.06);
  background: rgba(247, 243, 239, 0.82);
  backdrop-filter: blur(16px);
}

.brand {
  color: #a72a12;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-decoration: none;
}

.links {
  display: flex;
  gap: 28px;
  flex-wrap: wrap;
}

.links a,
.actions a {
  color: rgba(34, 34, 34, 0.62);
  text-decoration: none;
  transition: color 0.2s ease;
}

.links a.router-link-active,
.links a:hover,
.actions a:hover {
  color: #b73016;
}

.actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.primary {
  border: 0;
  border-radius: 999px;
  padding: 10px 18px;
  background: linear-gradient(135deg, #cb4326, #af250d);
  color: #fff;
  cursor: pointer;
  text-decoration: none;
  box-shadow: 0 10px 24px rgba(183, 45, 20, 0.2);
}

.points {
  color: #9e4a27;
  font-weight: 600;
}

@media (max-width: 900px) {
  .top-nav {
    flex-direction: column;
    align-items: flex-start;
    padding: 14px 0;
  }
}
</style>
