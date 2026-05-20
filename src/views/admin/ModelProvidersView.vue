<template>
  <section class="providers-page">
    <header class="head">
      <div>
        <h1>模型配置中心</h1>
        <p>管理多个 OpenAI-compatible provider，维护优先级、QPS、超时和状态。</p>
      </div>
      <button type="button" @click="createProvider">新增 Provider</button>
    </header>

    <div class="layout">
      <article class="panel table-panel">
        <table>
          <thead>
            <tr>
              <th>provider_name</th>
              <th>model_name</th>
              <th>base_url</th>
              <th>priority</th>
              <th>status</th>
              <th>qps_limit</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="provider in providers" :key="String(provider.id)" @click="fillForm(provider)">
              <td>{{ provider.provider_name }}</td>
              <td>{{ provider.model_name }}</td>
              <td>{{ provider.base_url }}</td>
              <td>{{ provider.priority }}</td>
              <td>{{ provider.status }}</td>
              <td>{{ provider.qps_limit }}</td>
            </tr>
          </tbody>
        </table>
      </article>

      <article class="panel form-panel">
        <strong>编辑 Provider</strong>
        <div class="form-grid">
          <input v-model="form.provider_id" placeholder="provider_id" />
          <input v-model="form.provider_name" placeholder="provider_name" />
          <input v-model="form.base_url" placeholder="base_url" />
          <input v-model="form.api_key_ref" placeholder="api_key_ref" />
          <input v-model="form.model_name" placeholder="model_name" />
          <input v-model="form.api_mode" placeholder="api_mode" />
          <input v-model="capabilitiesText" placeholder="capabilities，逗号分隔" />
          <input v-model.number="form.priority" placeholder="priority" />
          <input v-model="form.status" placeholder="status" />
          <input v-model.number="form.timeout_seconds" placeholder="timeout_seconds" />
          <input v-model.number="form.qps_limit" placeholder="qps_limit" />
          <input v-model="form.cost_level" placeholder="cost_level" />
        </div>
        <div class="actions">
          <button type="button" @click="saveProvider">{{ editingId ? "保存修改" : "创建" }}</button>
          <button type="button" class="ghost" @click="setMaintenance">设为 maintenance</button>
        </div>
        <p v-if="message" class="message">{{ message }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { ApiClient } from "@/api/client";
import { DreamDrawApi, type ModelProviderPayload } from "@/api/dream-draw";
import { useSessionStore } from "@/stores/session";

type ProviderRecord = Record<string, any>;

const session = useSessionStore();
const api = new DreamDrawApi(
  new ApiClient({
    getToken: () => session.adminToken,
  }),
);

const providers = ref<ProviderRecord[]>([]);
const editingId = ref<number | null>(null);
const message = ref("");

const form = ref<ModelProviderPayload>({
  provider_id: "",
  provider_name: "",
  base_url: "",
  api_key_ref: "",
  model_name: "",
  api_mode: "openai_compatible",
  capabilities: [],
  priority: 100,
  status: "healthy",
  timeout_seconds: 60,
  qps_limit: 5,
  cost_level: "medium",
});

const capabilitiesText = computed({
  get: () => form.value.capabilities.join(","),
  set: (value: string) => {
    form.value.capabilities = value.split(",").map((item) => item.trim()).filter(Boolean);
  },
});

function resetForm() {
  editingId.value = null;
  form.value = {
    provider_id: "",
    provider_name: "",
    base_url: "",
    api_key_ref: "",
    model_name: "",
    api_mode: "openai_compatible",
    capabilities: [],
    priority: 100,
    status: "healthy",
    timeout_seconds: 60,
    qps_limit: 5,
    cost_level: "medium",
  };
}

function fillForm(provider: ProviderRecord) {
  editingId.value = Number(provider.id);
  form.value = {
    provider_id: provider.provider_id,
    provider_name: provider.provider_name,
    base_url: provider.base_url,
    api_key_ref: provider.api_key_ref,
    model_name: provider.model_name,
    api_mode: provider.api_mode,
    capabilities: String(provider.capabilities || "").split(",").filter(Boolean),
    priority: Number(provider.priority),
    status: provider.status,
    timeout_seconds: Number(provider.timeout_seconds),
    qps_limit: Number(provider.qps_limit),
    cost_level: provider.cost_level,
  };
}

async function loadProviders() {
  const response = await api.getModelProviders();
  providers.value = response.providers;
}

function createProvider() {
  resetForm();
}

async function saveProvider() {
  if (editingId.value) {
    await api.updateModelProvider(editingId.value, form.value);
    message.value = "Provider 已更新";
  } else {
    await api.createModelProvider(form.value);
    message.value = "Provider 已创建";
  }
  await loadProviders();
}

async function setMaintenance() {
  if (!editingId.value) return;
  await api.updateModelProviderStatus(editingId.value, "maintenance");
  message.value = "Provider 状态已更新为 maintenance";
  await loadProviders();
}

onMounted(() => {
  void loadProviders();
});
</script>

<style scoped>
.head,
.layout {
  display: grid;
  gap: 16px;
}

.head {
  grid-template-columns: 1fr auto;
  align-items: start;
  margin-bottom: 18px;
}

.head h1 {
  margin: 0 0 6px;
  color: #1b2c40;
}

.head p,
.message {
  color: #6f8090;
}

.head button,
.actions button {
  border: 0;
  border-radius: 12px;
  padding: 10px 14px;
  background: #214e78;
  color: #fff;
}

.layout {
  grid-template-columns: 1.1fr 0.9fr;
}

.panel {
  padding: 20px;
  border-radius: 22px;
  background: #fff;
  border: 1px solid #e7edf3;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 12px 10px;
  border-bottom: 1px solid #eef3f8;
  text-align: left;
}

tbody tr {
  cursor: pointer;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.form-grid input {
  border: 1px solid #d5e0e9;
  border-radius: 12px;
  padding: 10px 12px;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}

.actions .ghost {
  background: #eef4fa;
  color: #315a80;
}

@media (max-width: 1100px) {
  .layout,
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
