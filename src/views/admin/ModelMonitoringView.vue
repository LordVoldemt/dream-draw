<template>
  <section class="monitoring-page">
    <header class="head">
      <div>
        <h1>模型状态监控</h1>
        <p>关注在线状态、成功率、延迟、超时次数、失败次数和审核拦截率。</p>
      </div>
      <button type="button" @click="loadMonitoring">刷新监控</button>
    </header>

    <div class="stats">
      <AdminStatCard label="healthy" :value="String(statusCount.healthy)" hint="正常可用模型数" />
      <AdminStatCard label="degraded" :value="String(statusCount.degraded)" hint="性能下降但仍可用" />
      <AdminStatCard label="maintenance" :value="String(statusCount.maintenance)" hint="人工维护状态" />
      <AdminStatCard label="unavailable" :value="String(statusCount.unavailable)" hint="不可用模型数" />
    </div>

    <article class="table-card">
      <table>
        <thead>
          <tr>
            <th>provider</th>
            <th>status</th>
            <th>成功率</th>
            <th>平均延迟</th>
            <th>超时次数</th>
            <th>失败次数</th>
            <th>审核拦截率</th>
            <th>排队数</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in monitoring" :key="String(item.provider_db_id)">
            <td>{{ item.provider_name }}</td>
            <td><span class="badge" :class="String(item.status)">{{ item.status }}</span></td>
            <td>{{ toPercent(item.success_rate) }}</td>
            <td>{{ item.average_latency_ms }} ms</td>
            <td>{{ item.timeout_count }}</td>
            <td>{{ item.failure_count }}</td>
            <td>{{ toPercent(item.blocked_rate) }}</td>
            <td>{{ item.queue_depth }}</td>
          </tr>
        </tbody>
      </table>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { ApiClient } from "@/api/client";
import { DreamDrawApi } from "@/api/dream-draw";
import AdminStatCard from "@/components/admin/AdminStatCard.vue";
import { useSessionStore } from "@/stores/session";

type MonitoringRecord = Record<string, any>;

const session = useSessionStore();
const api = new DreamDrawApi(
  new ApiClient({
    getToken: () => session.adminToken,
  }),
);

const monitoring = ref<MonitoringRecord[]>([]);

const statusCount = computed(() => {
  return {
    healthy: monitoring.value.filter((item) => item.status === "healthy").length,
    degraded: monitoring.value.filter((item) => item.status === "degraded").length,
    maintenance: monitoring.value.filter((item) => item.status === "maintenance").length,
    unavailable: monitoring.value.filter((item) => item.status === "unavailable").length,
  };
});

function toPercent(value: unknown) {
  return `${Math.round(Number(value || 0) * 100)}%`;
}

async function loadMonitoring() {
  const response = await api.getModelMonitoring();
  monitoring.value = response.monitoring;
}

onMounted(() => {
  void loadMonitoring();
});
</script>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.head h1 {
  margin: 0 0 6px;
  color: #1b2c40;
}

.head p {
  color: #6f8090;
}

.head button {
  border: 0;
  border-radius: 12px;
  padding: 10px 14px;
  background: #214e78;
  color: #fff;
}

.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 18px;
}

.table-card {
  overflow: auto;
  border-radius: 24px;
  background: #fff;
  border: 1px solid #e6edf4;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 12px 14px;
  border-bottom: 1px solid #eef3f8;
  text-align: left;
}

.badge {
  display: inline-flex;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
}

.badge.healthy {
  background: #e6f7ee;
  color: #2c8e58;
}

.badge.degraded {
  background: #fff1db;
  color: #b56a1c;
}

.badge.maintenance {
  background: #edf3f8;
  color: #607487;
}

.badge.unavailable {
  background: #fde8e8;
  color: #bc4b4b;
}

@media (max-width: 1100px) {
  .stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
