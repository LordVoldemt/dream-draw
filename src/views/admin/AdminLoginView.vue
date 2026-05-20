<template>
  <div class="admin-login-page">
    <section class="login-panel">
      <h1>绘梦管理后台</h1>
      <p>使用管理员账号登录后，可维护用户、模型配置和运行状态。</p>
      <form class="form" @submit.prevent="submitLogin">
        <input v-model="account" placeholder="管理员账号" />
        <input v-model="password" type="password" placeholder="管理员密码" />
        <button type="submit" :disabled="submitting">登录后台</button>
        <p v-if="message" class="message">{{ message }}</p>
      </form>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ApiClient } from "@/api/client";
import { DreamDrawApi } from "@/api/dream-draw";
import { useSessionStore } from "@/stores/session";

const router = useRouter();
const session = useSessionStore();
const api = new DreamDrawApi(
  new ApiClient({
    getToken: () => session.adminToken,
  }),
);

const account = ref("admin");
const password = ref("admin123");
const submitting = ref(false);
const message = ref("");

async function submitLogin() {
  submitting.value = true;
  message.value = "";
  try {
    const response = await api.adminLogin({
      account: account.value,
      password: password.value,
    });
    session.setAdminToken(response.token);
    await router.push("/admin");
  } catch (error) {
    message.value = error instanceof Error ? error.message : "登录失败";
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.admin-login-page {
  display: grid;
  place-items: center;
  min-height: 100vh;
}

.login-panel {
  width: min(480px, 100%);
  padding: 32px;
  border-radius: 28px;
  background: #fff;
  border: 1px solid #e7edf3;
}

.login-panel h1 {
  margin: 0 0 10px;
  color: #192b3f;
}

.login-panel p,
.message {
  color: #738291;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.form input {
  border: 1px solid #d6e1ea;
  border-radius: 14px;
  padding: 12px 14px;
}

.form button {
  border: 0;
  border-radius: 14px;
  padding: 12px 16px;
  background: #1f4d78;
  color: #fff;
  cursor: pointer;
}
</style>
