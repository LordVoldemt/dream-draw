<template>
  <section class="dashboard-page">
    <header class="head">
      <div>
        <h1>后台总览</h1>
        <p>聚合用户、作品、分享和模型运行状态，方便快速判断平台健康度。</p>
      </div>
      <button type="button" @click="loadOverview">刷新概览</button>
    </header>

    <div v-if="loading" class="state-card">正在加载后台概览...</div>
    <template v-else>
      <div class="stats">
        <AdminStatCard label="用户总数" :value="String(overview.users_total)" hint="累计注册手机号用户" />
        <AdminStatCard label="作品总数" :value="String(overview.works_total)" hint="已成功入库作品" />
        <AdminStatCard label="进行中任务" :value="String(overview.active_tasks_total)" hint="pending / generating / reviewing" />
        <AdminStatCard label="分享总数" :value="String(overview.shares_total)" hint="增长闭环分享事件" />
        <AdminStatCard label="收藏总数" :value="String(overview.favorites_total)" hint="用户收藏行为沉淀" />
        <AdminStatCard
          label="健康模型"
          :value="String(overview.provider_summary.healthy ?? 0)"
          hint="当前可优先承接生成请求"
        />
      </div>

      <article class="panel">
        <div class="section-head">
          <h2>模型状态摘要</h2>
          <span>{{ overview.providers.length }} 个 provider</span>
        </div>
        <div class="provider-grid">
          <div v-for="provider in overview.providers" :key="String(provider.provider_db_id)" class="provider-card">
            <div class="provider-title">
              <strong>{{ provider.provider_name }}</strong>
              <span class="badge" :class="String(provider.status)">{{ provider.status }}</span>
            </div>
            <p>{{ provider.model_name }}</p>
            <div class="provider-metrics">
              <span>成功率 {{ toPercent(provider.success_rate) }}</span>
              <span>延迟 {{ provider.average_latency_ms }} ms</span>
              <span>队列 {{ provider.queue_depth }}</span>
            </div>
          </div>
        </div>
      </article>
    </template>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ApiClient } from "@/api/client";
import { DreamDrawApi } from "@/api/dream-draw";
import AdminStatCard from "@/components/admin/AdminStatCard.vue";
import { useSessionStore } from "@/stores/session";

const session = useSessionStore();
const api = new DreamDrawApi(
  new ApiClient({
    getToken: () => session.adminToken,
  }),
);

const loading = ref(true);
type OverviewState = {
  users_total: number;
  works_total: number;
  active_tasks_total: number;
  favorites_total: number;
  shares_total: number;
  provider_summary: {
    healthy: number;
    degraded: number;
    maintenance: number;
    unavailable: number;
  };
  providers: Array<Record<string, unknown>>;
};

const overview = ref({
  users_total: 0,
  works_total: 0,
  active_tasks_total: 0,
  favorites_total: 0,
  shares_total: 0,
  provider_summary: {
    healthy: 0,
    degraded: 0,
    maintenance: 0,
    unavailable: 0,
  },
  providers: [] as Array<Record<string, unknown>>,
} satisfies OverviewState);

function toPercent(value: unknown) {
  return `${Math.round(Number(value || 0) * 100)}%`;
}

async function loadOverview() {
  loading.value = true;
  try {
    const response = await api.getAdminOverview();
    overview.value = {
      ...response.overview,
      provider_summary: {
        healthy: response.overview.provider_summary.healthy ?? 0,
        degraded: response.overview.provider_summary.degraded ?? 0,
        maintenance: response.overview.provider_summary.maintenance ?? 0,
        unavailable: response.overview.provider_summary.unavailable ?? 0,
      },
    };
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void loadOverview();
});
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.head h1 {
  margin: 0 0 6px;
  color: #1b2c40;
}

.head p,
.state-card {
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
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.state-card,
.panel {
  padding: 20px;
  border-radius: 22px;
  background: #fff;
  border: 1px solid #e7edf3;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.section-head h2 {
  margin: 0;
}

.provider-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.provider-card {
  padding: 16px;
  border-radius: 16px;
  background: #f8fbfd;
  border: 1px solid #e6edf4;
}

.provider-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.provider-title strong {
  color: #223447;
}

.provider-card p {
  margin: 8px 0 12px;
  color: #6f8090;
}

.provider-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: #37506b;
  font-size: 14px;
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
  .stats,
  .provider-grid {
    grid-template-columns: 1fr;
  }
}
</style>
