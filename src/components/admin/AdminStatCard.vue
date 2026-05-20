<template>
  <article class="stat-card">
    <p class="label">{{ label }}</p>
    <strong class="value">{{ value }}</strong>
    <span v-if="hint" class="hint">{{ hint }}</span>
  </article>
</template>

<script setup lang="ts">
defineProps<{
  label: string;
  value: string;
  hint?: string;
}>();
</script>

<style scoped>
.stat-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
  padding: 18px 20px;
  border-radius: 20px;
  background: #fff;
  border: 1px solid #e7edf3;
}

.label {
  margin: 0;
  color: #6c7c8b;
  font-size: 13px;
}

.value {
  color: #16283b;
  font-size: 28px;
}

.hint {
  color: #94a2af;
  font-size: 12px;
}
</style>
