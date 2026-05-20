<template>
  <section class="detail-page">
    <div v-if="loading" class="state-card">用户详情加载中...</div>
    <template v-else-if="detail">
      <header class="page-head">
        <div class="head-copy">
          <div class="breadcrumb">管理后台 〉 用户管理</div>
          <div class="title-row">
            <h1>用户详情</h1>
            <span class="uid-pill">UID: {{ detail.user.id }}</span>
          </div>
        </div>
        <div class="head-actions">
          <button type="button" class="ghost-button">查看审计日志</button>
          <button type="button" class="ghost-button" @click="toggleStatus">
            {{ detail.user.status === "frozen" ? "解冻账号" : "冻结账号" }}
          </button>
          <button type="button" class="primary-button" @click="adjustPoints(50)">调整算力点数</button>
        </div>
      </header>

      <div class="content-grid">
        <div class="left-column">
          <article class="panel profile-panel">
            <div class="profile-top">
              <div class="avatar-box">青</div>
              <div class="identity-block">
                <strong>{{ detail.user.nickname }} ({{ romanizedName }})</strong>
                <p>加入时间：{{ joinDate }}</p>
              </div>
            </div>

            <div class="profile-grid">
              <div>
                <span class="label">电子邮箱</span>
                <p>{{ detail.user.masked_email || "qingdai.yu@dreamink.ai" }}</p>
              </div>
              <div>
                <span class="label">手机号码</span>
                <p>{{ detail.user.masked_phone }}</p>
              </div>
              <div>
                <span class="label">账号等级</span>
                <p class="highlight">★ 高级创作者</p>
              </div>
              <div>
                <span class="label">实名认证</span>
                <p class="verified">已认证</p>
              </div>
            </div>
          </article>

          <article class="panel points-panel">
            <div class="points-head">
              <div>
                <span class="label">算力点数余额</span>
                <div class="points-total">
                  <strong>{{ detail.user.points_balance }}</strong>
                  <span>Points</span>
                </div>
              </div>
              <button type="button" class="text-button">导出记录</button>
            </div>

            <table v-if="detail.points_transactions.length > 0">
              <thead>
                <tr>
                  <th>变更原因</th>
                  <th>数值变动</th>
                  <th>发生时间</th>
                  <th>状态</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in detail.points_transactions" :key="String(item.id)">
                  <td>{{ item.reason }}</td>
                  <td :class="Number(item.delta) >= 0 ? 'delta-positive' : 'delta-negative'">
                    {{ Number(item.delta) >= 0 ? `+${item.delta}` : item.delta }}
                  </td>
                  <td>{{ formatDateTime(String(item.created_at)) }}</td>
                  <td><span class="status-tag">成功</span></td>
                </tr>
              </tbody>
            </table>
            <div v-else class="empty-tip">暂无积分流水记录</div>
          </article>
        </div>

        <aside class="right-column">
          <article class="panel creation-panel">
            <div class="side-head">
              <h2>创作记录</h2>
              <a href="#">查看全部</a>
            </div>
            <div class="creation-grid">
              <div v-for="item in creations" :key="item.title" class="creation-card">
                <img :src="item.image" :alt="item.title" />
                <span>{{ item.title }}</span>
              </div>
            </div>

            <div class="stats-block">
              <h3>创作统计</h3>
              <div class="stat-row">
                <span>总生成次数</span>
                <strong>428</strong>
              </div>
              <div class="stat-row">
                <span>收藏率</span>
                <strong>15%</strong>
              </div>
              <div class="stat-row">
                <span>常用风格</span>
                <strong class="accent">敦煌重彩</strong>
              </div>
            </div>
          </article>
        </aside>
      </div>

      <p v-if="message" class="message">{{ message }}</p>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { ApiClient } from "@/api/client";
import { DreamDrawApi } from "@/api/dream-draw";
import { useSessionStore } from "@/stores/session";

type DetailRecord = {
  user: Record<string, any>;
  points_transactions: Array<Record<string, any>>;
};

const route = useRoute();
const session = useSessionStore();
const api = new DreamDrawApi(
  new ApiClient({
    getToken: () => session.adminToken,
  }),
);

const loading = ref(true);
const detail = ref<DetailRecord | null>(null);
const message = ref("");

const romanizedName = computed(() => "Qing Dai");
const joinDate = computed(() => "2023年11月14日");

const creations = [
  {
    title: "敦煌飞天系列 #01",
    image: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=700&q=80",
  },
  {
    title: "盛世繁花 #12",
    image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=700&q=80",
  },
  {
    title: "山外青山 #08",
    image: "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=700&q=80",
  },
  {
    title: "意象书法 #03",
    image: "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=700&q=80",
  },
];

async function loadDetail() {
  loading.value = true;
  try {
    detail.value = await api.getAdminUserDetail(Number(route.params.id));
  } finally {
    loading.value = false;
  }
}

function formatDateTime(value: string) {
  return value ? value.replace("T", " ").slice(0, 16) : "--";
}

async function adjustPoints(delta: number) {
  if (!detail.value) return;
  await api.updateAdminUserPoints(Number(route.params.id), {
    delta,
    reason: "运营补偿",
    confirm: true,
  });
  message.value = "积分调整成功";
  await loadDetail();
}

async function toggleStatus() {
  if (!detail.value) return;
  const nextStatus = detail.value.user.status === "frozen" ? "active" : "frozen";
  await api.updateAdminUserStatus(Number(route.params.id), {
    status: nextStatus,
    reason: "后台人工维护",
    confirm: true,
  });
  message.value = `用户状态已更新为 ${nextStatus}`;
  await loadDetail();
}

onMounted(() => {
  void loadDetail();
});
</script>

<style scoped>
.detail-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.state-card,
.panel {
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 40px rgba(31, 26, 22, 0.05);
}

.state-card {
  padding: 32px;
  color: #675750;
}

.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.breadcrumb {
  color: #71615a;
  font-size: 16px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 18px;
}

.title-row h1 {
  margin: 0;
  color: #1c1917;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 34px;
}

.uid-pill {
  display: inline-flex;
  align-items: center;
  min-height: 42px;
  padding: 0 18px;
  border-radius: 999px;
  background: #eff6f2;
  color: #688778;
  font-size: 16px;
}

.head-actions {
  display: flex;
  gap: 14px;
}

.ghost-button,
.primary-button {
  min-width: 170px;
  height: 58px;
  border-radius: 14px;
  font-size: 18px;
  cursor: pointer;
}

.ghost-button {
  border: 1px solid rgba(228, 220, 213, 0.92);
  background: #fff;
  color: #2d2522;
}

.primary-button {
  border: 0;
  background: linear-gradient(135deg, #d1492b, #c63f22);
  color: #fff;
  box-shadow: 0 16px 30px rgba(198, 63, 34, 0.16);
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) 440px;
  gap: 24px;
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-panel,
.points-panel,
.creation-panel {
  padding: 28px 30px;
}

.profile-top {
  display: flex;
  gap: 22px;
  align-items: center;
}

.avatar-box {
  display: grid;
  place-items: center;
  width: 156px;
  height: 156px;
  border-radius: 20px;
  background: linear-gradient(135deg, #f9fbfa, #e6efe8);
  color: #4d7f70;
  font-size: 48px;
}

.identity-block strong {
  display: block;
  color: #221c1a;
  font-size: 20px;
}

.identity-block p {
  margin: 8px 0 0;
  color: #675751;
  font-size: 16px;
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px 36px;
  margin-top: 30px;
}

.label {
  display: block;
  margin-bottom: 10px;
  color: #6e5f58;
  font-size: 16px;
}

.profile-grid p {
  margin: 0;
  color: #241d1a;
  font-size: 18px;
}

.highlight {
  color: #d2a629 !important;
  font-weight: 700;
}

.verified {
  color: #6b8a7b !important;
}

.points-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}

.points-total {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-top: 8px;
}

.points-total strong {
  color: #d1492b;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 56px;
  line-height: 1;
}

.points-total span {
  color: #4c3d38;
  font-size: 18px;
}

.text-button {
  border: 0;
  background: transparent;
  color: #6d887a;
  font-size: 16px;
  cursor: pointer;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 18px 10px;
  border-bottom: 1px solid rgba(239, 234, 229, 0.92);
  text-align: left;
}

th {
  color: #7a6961;
  font-size: 16px;
  font-weight: 600;
}

td {
  color: #2d2421;
  font-size: 18px;
}

.delta-positive {
  color: #5f8b78;
  font-weight: 700;
}

.delta-negative {
  color: #d1492b;
  font-weight: 700;
}

.status-tag {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  background: #edf7f1;
  color: #6b8a7b;
  font-size: 14px;
}

.side-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}

.side-head h2,
.stats-block h3 {
  margin: 0;
  color: #201b19;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 28px;
}

.side-head a {
  color: #5a4d47;
  text-decoration: none;
}

.creation-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.creation-card {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
}

.creation-card img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
}

.creation-card span {
  position: absolute;
  left: 14px;
  bottom: 12px;
  color: #fff;
  font-size: 14px;
}

.stats-block {
  margin-top: 26px;
  padding-top: 24px;
  border-top: 1px solid rgba(239, 234, 229, 0.92);
}

.stat-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 18px;
  color: #4f423c;
  font-size: 18px;
}

.stat-row strong {
  color: #231d1a;
}

.stat-row .accent {
  color: #d2a629;
}

.message {
  margin: 0;
  color: #685851;
}

@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 960px) {
  .page-head,
  .head-actions,
  .profile-grid {
    flex-direction: column;
    grid-template-columns: 1fr;
  }

  .head-actions {
    width: 100%;
  }

  .creation-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
