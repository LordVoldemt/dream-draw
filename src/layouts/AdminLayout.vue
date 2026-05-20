<template>
  <div class="admin-layout">
    <aside class="layout-sidebar">
      <div class="brand-wrap">
        <div class="brand">墨染梦境</div>
        <div class="sub-brand">AI艺术工坊</div>
      </div>
      <nav class="sidebar-nav">
        <RouterLink to="/admin">控制台</RouterLink>
        <RouterLink to="/admin/users">用户管理</RouterLink>
        <RouterLink to="/admin/model-providers">模型配置</RouterLink>
        <RouterLink to="/admin/model-monitoring">模型监控</RouterLink>
      </nav>
      <div class="help-link">帮助中心</div>
    </aside>
    <section class="layout-main">
      <RouterView />
    </section>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from "vue-router";
import { RouterLink } from "vue-router";
</script>

<style scoped>
.admin-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  min-height: 100vh;
  background: #f7f4f0;
}

.layout-sidebar {
  display: flex;
  flex-direction: column;
  padding: 34px 28px;
  background: #fbf8f4;
  border-right: 1px solid rgba(225, 219, 214, 0.9);
  color: #332824;
}

.brand-wrap {
  margin-bottom: 28px;
}

.brand {
  color: #d24729;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 28px;
  font-weight: 600;
}

.sub-brand {
  margin-top: 8px;
  color: #8d7e76;
  font-size: 18px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.sidebar-nav a {
  color: #6c5d55;
  text-decoration: none;
  font-size: 18px;
}

.sidebar-nav a.router-link-active {
  color: #d24729;
}

.help-link {
  margin-top: auto;
  color: #65564e;
  font-size: 18px;
}

.layout-main {
  padding: 42px 48px 32px;
}
</style>
