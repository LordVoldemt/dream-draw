<template>
  <div class="user-layout">
    <TopNavBar v-if="!isImmersivePage" class="layout-header" />
    <main class="layout-content" :class="{ 'layout-content--immersive': isImmersivePage }">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterView, useRoute } from "vue-router";
import TopNavBar from "@/components/user/TopNavBar.vue";

const route = useRoute();
const immersivePages = new Set(["login", "register", "generating"]);
const isImmersivePage = computed(() => immersivePages.has(String(route.name ?? "")));
</script>

<style scoped>
.user-layout {
  min-height: 100vh;
  background: linear-gradient(180deg, #fff8f3 0%, #f7efe6 100%);
}

.layout-header {
  margin: 24px 32px 0;
}

.layout-content {
  padding: 24px 32px 48px;
}

.layout-content--immersive {
  padding: 0;
}
</style>
