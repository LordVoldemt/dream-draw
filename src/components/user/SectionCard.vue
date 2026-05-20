<template>
  <section class="section-card">
    <header v-if="title || subtitle" class="section-head">
      <h2 v-if="title">{{ title }}</h2>
      <p v-if="subtitle">{{ subtitle }}</p>
    </header>
    <slot />
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title?: string;
  subtitle?: string;
}>();
</script>

<style scoped>
.section-card {
  border: 1px solid rgba(121, 79, 42, 0.12);
  border-radius: 28px;
  padding: 24px;
  background: rgba(255, 251, 247, 0.92);
  box-shadow: 0 18px 40px rgba(116, 76, 35, 0.08);
}

.section-head {
  margin-bottom: 18px;
}

.section-head h2 {
  margin: 0 0 8px;
  color: #5d2d1a;
  font-size: 24px;
}

.section-head p {
  margin: 0;
  color: #7a6657;
  line-height: 1.6;
}
</style>
