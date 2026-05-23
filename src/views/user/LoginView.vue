<template>
  <div class="login-page">
    <div class="page-background"></div>
    <div class="page-overlay"></div>

    <div class="login-shell">
      <header class="brand-block">
        <h1>绘梦</h1>
        <p>INK DREAM UNIVERSE</p>
      </header>

      <section class="login-card">
        <form class="form" @submit.prevent="submitLogin">
          <label class="field">
            <span class="field-label">手机号</span>
            <input v-model="phone" maxlength="11" placeholder="请输入您的手机号" />
          </label>

          <label class="field">
            <span class="field-label">验证码</span>
            <div class="code-row">
              <input v-model="code" maxlength="6" placeholder="请输入验证码" />
              <button
                class="secondary"
                type="button"
                :disabled="sendingCode || countdown > 0"
                @click="sendCode"
              >
                {{ countdown > 0 ? `${countdown}s` : "获取验证码" }}
              </button>
            </div>
          </label>

          <div v-if="mockCode" class="mock-tip">开发环境验证码：{{ mockCode }}</div>

          <button class="primary" type="submit" :disabled="submitting">
            <span>确认进入</span>
            <span class="arrow">→</span>
          </button>

          <p v-if="message" class="message">{{ message }}</p>
        </form>

        <div class="card-divider"></div>

        <div class="card-footer">
          <a href="#">忘记密码？</a>
          <div class="register-tip">
            <span>还没有账号？</span>
            <RouterLink to="/register">立即注册</RouterLink>
          </div>
        </div>
      </section>

      <p class="copyright">© 2024 绘梦 Ink Dream AI. All Rights Reserved.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { ApiClient } from "@/api/client";
import { DreamDrawApi } from "@/api/dream-draw";
import { useSessionStore } from "@/stores/session";

const route = useRoute();
const router = useRouter();
const session = useSessionStore();
const api = new DreamDrawApi(
  new ApiClient({
    getToken: () => session.userToken,
  }),
);

const phone = ref("");
const code = ref("");
const sendingCode = ref(false);
const submitting = ref(false);
const countdown = ref(0);
const message = ref("");
const mockCode = ref("");
const redirectPath = computed(() => (route.query.redirect as string) || "/workspace");
let timer: number | null = null;

async function sendCode() {
  if (!/^\d{11}$/.test(phone.value)) {
    message.value = "请输入 11 位手机号。";
    return;
  }
  sendingCode.value = true;
  message.value = "";
  try {
    const response = await api.sendSmsCode(phone.value);
    mockCode.value = response.mock_code;
    countdown.value = response.cooldown_seconds;
    timer = window.setInterval(() => {
      countdown.value -= 1;
      if (countdown.value <= 0 && timer !== null) {
        window.clearInterval(timer);
        timer = null;
      }
    }, 1000);
  } catch (error) {
    message.value = error instanceof Error ? error.message : "验证码发送失败";
  } finally {
    sendingCode.value = false;
  }
}

async function submitLogin() {
  if (!/^\d{11}$/.test(phone.value) || code.value.length < 4) {
    message.value = "请填写正确的手机号和验证码。";
    return;
  }
  submitting.value = true;
  message.value = "";
  try {
    const response = await api.login({ phone: phone.value, code: code.value });
    session.setUserToken(response.token);
    session.setUserProfile({
      phone: response.user.phone,
      pointsBalance: response.user.points_balance,
    });
    if (response.is_first_login) {
      message.value = "首登成功，已为你发放 10 积分。";
      await router.push("/reward");
      return;
    }
    message.value = "登录成功，正在返回生成流程。";
    await router.push(redirectPath.value);
  } catch (error) {
    message.value = error instanceof Error ? error.message : "登录失败";
  } finally {
    submitting.value = false;
  }
}

onBeforeUnmount(() => {
  if (timer !== null) {
    window.clearInterval(timer);
  }
});
</script>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  margin: -24px -32px -48px;
}

.page-background,
.page-overlay {
  position: absolute;
  inset: 0;
}

.page-background {
  background:
    linear-gradient(rgba(248, 243, 234, 0.14), rgba(248, 243, 234, 0.14)),
    url("https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1800&q=80")
      center/cover no-repeat;
  transform: scale(1.03);
}

.page-overlay {
  background:
    radial-gradient(circle at top center, rgba(255, 244, 217, 0.72), transparent 42%),
    linear-gradient(180deg, rgba(255, 250, 240, 0.12), rgba(67, 87, 82, 0.2));
}

.login-shell {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  padding: 74px 20px 32px;
}

.brand-block {
  text-align: center;
  margin-bottom: 34px;
}

.brand-block h1 {
  margin: 0;
  color: #d64526;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 58px;
  line-height: 1.08;
}

.brand-block p {
  margin: 12px 0 0;
  color: rgba(35, 35, 35, 0.66);
  font-size: 21px;
  letter-spacing: 0.28em;
}

.login-card {
  width: min(560px, calc(100vw - 40px));
  display: flex;
  flex-direction: column;
  padding: 44px 48px 32px;
  border-radius: 28px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.84), rgba(255, 255, 255, 0.72));
  border: 1px solid rgba(255, 255, 255, 0.48);
  box-shadow:
    0 30px 60px rgba(69, 82, 69, 0.18),
    0 0 80px rgba(235, 210, 133, 0.18);
  backdrop-filter: blur(16px);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 26px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field-label {
  color: #5d443a;
  font-size: 18px;
}

.form input {
  height: 64px;
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 14px;
  padding: 0 22px;
  background: rgba(255, 255, 255, 0.52);
  color: #3a302c;
  font-size: 18px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.78);
}

.form input::placeholder {
  color: rgba(74, 63, 58, 0.62);
}

.code-row {
  display: grid;
  grid-template-columns: 1fr 144px;
  gap: 12px;
}

.primary,
.secondary {
  border-radius: 14px;
  cursor: pointer;
  font-size: 18px;
}

.primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  height: 76px;
  margin-top: 14px;
  border: 0;
  background: linear-gradient(135deg, #d9482b, #c5391e);
  color: #fff;
  font-size: 22px;
  font-weight: 600;
  box-shadow: 0 18px 36px rgba(202, 64, 37, 0.26);
}

.secondary {
  height: 64px;
  border: 1px solid rgba(217, 72, 43, 0.26);
  background: rgba(255, 248, 244, 0.76);
  color: #d6482b;
}

.secondary:disabled,
.primary:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.arrow {
  font-size: 28px;
  line-height: 1;
}

.message,
.mock-tip {
  color: #8f4e32;
  font-size: 14px;
}

.card-divider {
  height: 1px;
  margin: 34px 0 28px;
  background: rgba(133, 116, 105, 0.2);
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  color: #5e4d45;
  font-size: 16px;
}

.card-footer a {
  color: #5e4d45;
  text-decoration: none;
}

.register-tip {
  display: flex;
  gap: 12px;
  align-items: center;
}

.register-tip a {
  color: #d64626;
  font-weight: 600;
  text-decoration: none;
}

.copyright {
  margin: 30px 0 0;
  color: rgba(49, 49, 49, 0.48);
  font-size: 14px;
  text-align: center;
}

@media (max-width: 720px) {
  .brand-block h1 {
    font-size: 42px;
  }

  .brand-block p {
    font-size: 16px;
    letter-spacing: 0.2em;
  }

  .login-card {
    padding: 28px 22px 24px;
  }

  .form {
    gap: 20px;
  }

  .field-label,
  .form input,
  .secondary,
  .card-footer {
    font-size: 16px;
  }

  .form input,
  .secondary {
    height: 56px;
  }

  .code-row {
    grid-template-columns: 1fr;
  }

  .primary {
    height: 64px;
    font-size: 20px;
  }

  .card-footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
