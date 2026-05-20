<template>
  <section class="admin-page">
    <header class="page-head">
      <div>
        <h1>用户管理</h1>
        <p>管理并监控您的数字水墨社区。</p>
      </div>
      <div class="head-actions">
        <button type="button" class="ghost-button">导出数据</button>
        <button type="button" class="primary-button">创建用户</button>
      </div>
    </header>

    <section class="toolbar-card">
      <div class="search-box">
        <span class="search-icon">⌕</span>
        <input v-model="keyword" placeholder="通过 ID、手机号或邮箱搜索..." />
      </div>
      <select v-model="status" class="filter-select">
        <option value="">状态：全部</option>
        <option value="active">状态：活跃</option>
        <option value="frozen">状态：已冻结</option>
      </select>
      <select v-model="orderBy" class="filter-select">
        <option value="latest">注册时间：最新</option>
        <option value="earliest">注册时间：最早</option>
      </select>
    </section>

    <div v-if="loading" class="state-card">用户数据加载中...</div>
    <section v-else class="table-card">
      <table>
        <thead>
          <tr>
            <th>用户 ID</th>
            <th>用户信息</th>
            <th>积分余额</th>
            <th>状态</th>
            <th>最后登录</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in orderedUsers" :key="String(user.id)">
            <td class="id-cell">#ID-<br />{{ user.id }}</td>
            <td>
              <div class="user-cell">
                <div class="avatar">{{ String(user.nickname ?? "?").slice(0, 1) }}</div>
                <div>
                  <strong>{{ user.nickname }}</strong>
                  <p>{{ user.masked_phone || user.masked_email || user.login_type }}</p>
                </div>
              </div>
            </td>
            <td class="points-cell">{{ user.points_balance }}</td>
            <td>
              <span class="status-pill" :class="String(user.status)">{{ statusLabel(String(user.status)) }}</span>
            </td>
            <td class="login-cell">{{ formatLastLogin(String(user.last_login_at ?? "")) }}</td>
            <td>
              <div class="action-cell">
                <RouterLink :to="`/admin/users/${user.id}`">◉</RouterLink>
                <button type="button" @click="quickToggle(user)">
                  {{ String(user.status) === "frozen" ? "↺" : "✳" }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <footer class="table-footer">
        <span>显示 {{ summaryText }}</span>
        <div class="pagination">
          <button type="button">‹</button>
          <button type="button" class="active">1</button>
          <button type="button">2</button>
          <button type="button">3</button>
          <span>…</span>
          <button type="button">124</button>
          <button type="button">›</button>
        </div>
      </footer>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { ApiClient } from "@/api/client";
import { DreamDrawApi } from "@/api/dream-draw";
import { useSessionStore } from "@/stores/session";

type AdminUser = Record<string, unknown>;

const session = useSessionStore();
const api = new DreamDrawApi(
  new ApiClient({
    getToken: () => session.adminToken,
  }),
);

const keyword = ref("");
const status = ref("");
const orderBy = ref("latest");
const loading = ref(true);
const users = ref<AdminUser[]>([]);

const filteredUsers = computed(() => {
  const q = keyword.value.trim().toLowerCase();
  let result = [...users.value];

  if (q) {
    result = result.filter((user) => {
      return [
        String(user.id ?? ""),
        String(user.nickname ?? ""),
        String(user.masked_phone ?? ""),
        String(user.masked_email ?? ""),
        String(user.login_type ?? ""),
      ]
        .join(" ")
        .toLowerCase()
        .includes(q);
    });
  }

  if (status.value) {
    result = result.filter((user) => String(user.status) === status.value);
  }

  return result;
});

const orderedUsers = computed(() => {
  const result = [...filteredUsers.value];
  result.sort((a, b) => {
    const aTime = String(a.last_login_at ?? "");
    const bTime = String(b.last_login_at ?? "");
    return orderBy.value === "earliest" ? aTime.localeCompare(bTime) : bTime.localeCompare(aTime);
  });
  return result;
});

const summaryText = computed(() => {
  const total = orderedUsers.value.length;
  return `${total} 名用户中的第 1-${Math.min(10, total)} 名`;
});

function statusLabel(value: string) {
  if (value === "active") return "活跃";
  if (value === "frozen") return "已冻结";
  return value;
}

function formatLastLogin(value: string) {
  if (!value) return "--";
  return value.replace("T", "\n").slice(0, 16);
}

async function loadUsers() {
  loading.value = true;
  try {
    const response = await api.getAdminUsers(keyword.value, status.value);
    users.value = response.users;
  } finally {
    loading.value = false;
  }
}

async function quickToggle(user: AdminUser) {
  const current = String(user.status ?? "");
  const nextStatus = current === "frozen" ? "active" : "frozen";
  await api.updateAdminUserStatus(Number(user.id), {
    status: nextStatus,
    reason: "后台快捷维护",
    confirm: true,
  });
  await loadUsers();
}

onMounted(() => {
  void loadUsers();
});
</script>

<style scoped>
.admin-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.page-head h1 {
  margin: 0 0 10px;
  color: #1e1b19;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 34px;
}

.page-head p {
  margin: 0;
  color: #6d5d56;
  font-size: 16px;
}

.head-actions {
  display: flex;
  gap: 14px;
}

.ghost-button,
.primary-button {
  min-width: 148px;
  height: 58px;
  border-radius: 14px;
  font-size: 18px;
  cursor: pointer;
}

.ghost-button {
  border: 1px solid rgba(228, 220, 213, 0.92);
  background: #fff;
  color: #2e2623;
}

.primary-button {
  border: 0;
  background: linear-gradient(135deg, #d1492b, #c63f22);
  color: #fff;
  box-shadow: 0 16px 30px rgba(198, 63, 34, 0.16);
}

.toolbar-card,
.table-card,
.state-card {
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 40px rgba(31, 26, 22, 0.05);
}

.toolbar-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 184px 228px;
  gap: 18px;
  padding: 28px 30px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 14px;
  height: 58px;
  padding: 0 18px;
  border: 1px solid rgba(232, 226, 220, 0.95);
  border-radius: 14px;
}

.search-box input {
  width: 100%;
  border: 0;
  outline: 0;
  color: #2c231f;
  font-size: 18px;
}

.search-icon {
  color: #a2958d;
  font-size: 26px;
}

.filter-select {
  height: 58px;
  padding: 0 18px;
  border: 1px solid rgba(232, 226, 220, 0.95);
  border-radius: 14px;
  background: #fff;
  color: #554742;
  font-size: 16px;
}

.state-card {
  padding: 32px;
  color: #64534c;
}

.table-card {
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 24px 30px;
  border-bottom: 1px solid rgba(239, 234, 229, 0.92);
  text-align: left;
  vertical-align: middle;
}

th {
  color: #7a6961;
  font-size: 16px;
  font-weight: 600;
}

td {
  color: #332925;
  font-size: 18px;
}

.id-cell,
.login-cell {
  color: #5f4e47;
  line-height: 1.55;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 14px;
}

.avatar {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #d9efe8, #fef8e7);
  color: #4d7f70;
  font-size: 18px;
}

.user-cell strong {
  display: block;
  margin-bottom: 4px;
  color: #2a211e;
  font-size: 20px;
}

.user-cell p {
  margin: 0;
  color: #93857d;
  font-size: 14px;
}

.points-cell {
  color: #567f71;
  font-size: 18px;
  font-weight: 700;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 0 16px;
  border-radius: 999px;
  font-size: 16px;
}

.status-pill.active {
  background: #d8f4e7;
  color: #4a7a69;
}

.status-pill.frozen {
  background: #ffe2e2;
  color: #c14f4f;
}

.action-cell {
  display: flex;
  gap: 16px;
}

.action-cell a,
.action-cell button {
  border: 0;
  background: transparent;
  color: #513d38;
  font-size: 24px;
  text-decoration: none;
  cursor: pointer;
}

.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 20px 30px;
  color: #6f5f58;
  font-size: 16px;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pagination button {
  width: 40px;
  height: 40px;
  border: 1px solid rgba(232, 226, 220, 0.95);
  border-radius: 8px;
  background: #fff;
  color: #574741;
  cursor: pointer;
}

.pagination button.active {
  border-color: #d1492b;
  background: #d1492b;
  color: #fff;
}

.pagination span {
  color: #7c6b63;
}

@media (max-width: 1200px) {
  .toolbar-card {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 960px) {
  .page-head,
  .table-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .head-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .table-card {
    overflow: auto;
  }
}
</style>
