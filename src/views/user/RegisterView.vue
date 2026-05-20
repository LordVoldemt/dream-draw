<template>
  <div class="register-page">
    <div class="page-background"></div>
    <div class="page-overlay"></div>
    <div class="lotus lotus-left"></div>
    <div class="lotus lotus-right"></div>

    <div class="register-shell">
      <section class="register-card">
        <div class="card-glow">LOGIN</div>

        <header class="hero-copy">
          <p class="hero-title">欢迎创建你的</p>
          <p class="hero-title hero-title--accent">专属国风身份</p>
          <span class="hero-divider"></span>
        </header>

        <div class="reward-pill">
          <span class="gift-icon">🎁</span>
          <span>新人礼遇：注册即送 <strong>10</strong> 次免费生成机会</span>
        </div>

        <form class="register-form" @submit.prevent="submitRegister">
          <label class="field">
            <span class="field-label">手机号</span>
            <div class="input-shell">
              <span class="field-icon">📱</span>
              <input v-model="phone" maxlength="11" placeholder="请输入您的手机号" />
            </div>
          </label>

          <label class="field">
            <span class="field-label">验证码</span>
            <div class="code-row">
              <div class="input-shell">
                <span class="field-icon">🛡</span>
                <input v-model="code" maxlength="6" placeholder="请输入验证码" />
              </div>
              <button
                class="secondary-button"
                type="button"
                :disabled="sendingCode || countdown > 0"
                @click="sendCode"
              >
                {{ countdown > 0 ? `${countdown}s` : "获取验证码" }}
              </button>
            </div>
          </label>

          <p v-if="mockCode" class="mock-tip">开发环境验证码：{{ mockCode }}</p>

          <label class="agreement">
            <input v-model="agreed" type="checkbox" />
            <span>我已阅读并同意《使用协议》与《隐私政策》，开启我的梦境之旅。</span>
          </label>

          <p v-if="message" class="message">{{ message }}</p>

          <button class="primary-button" type="submit" :disabled="submitting || !agreed">
            <span>立即注册并领取奖励</span>
            <span class="sparkle">✦</span>
          </button>
        </form>

        <footer class="card-footer">
          <span>已有账号？</span>
          <RouterLink to="/login">立即登录</RouterLink>
        </footer>
      </section>
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
const agreed = ref(true);
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
    message.value = error instanceof Error ? error.message : "验证码发送失败。";
  } finally {
    sendingCode.value = false;
  }
}

async function submitRegister() {
  if (!agreed.value) {
    message.value = "请先勾选协议后再继续。";
    return;
  }
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
      message.value = "注册成功，10 次免费生成机会已发放。";
      await router.push("/reward");
      return;
    }
    message.value = "该手机号已注册，正在为你登录。";
    await router.push(redirectPath.value);
  } catch (error) {
    message.value = error instanceof Error ? error.message : "注册失败，请稍后再试。";
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
.register-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

.page-background,
.page-overlay {
  position: absolute;
  inset: 0;
}

.page-background {
  background:
    linear-gradient(rgba(255, 250, 241, 0.18), rgba(255, 250, 241, 0.18)),
    url("https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1800&q=80")
      center/cover no-repeat;
  transform: scale(1.04);
  filter: saturate(0.88) brightness(1.08);
}

.page-overlay {
  background:
    radial-gradient(circle at 50% 14%, rgba(255, 242, 198, 0.82), transparent 34%),
    linear-gradient(180deg, rgba(255, 250, 237, 0.18), rgba(64, 91, 98, 0.22));
}

.lotus {
  position: absolute;
  bottom: -40px;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background:
    radial-gradient(circle, rgba(255, 247, 224, 0.96) 0 16%, transparent 17%),
    radial-gradient(circle at 50% 62%, rgba(255, 255, 255, 0.92) 0 24%, transparent 25%),
    radial-gradient(circle at 20% 60%, rgba(200, 62, 38, 0.9) 0 20%, transparent 21%),
    radial-gradient(circle at 80% 68%, rgba(215, 88, 56, 0.72) 0 14%, transparent 15%);
  opacity: 0.9;
  filter: blur(0.4px);
}

.lotus-left {
  left: -36px;
}

.lotus-right {
  right: -26px;
}

.register-shell {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 36px 20px;
}

.register-card {
  position: relative;
  width: min(620px, calc(100vw - 40px));
  padding: 56px 50px 44px;
  border-radius: 26px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.84), rgba(255, 255, 255, 0.7));
  border: 1px solid rgba(255, 236, 214, 0.9);
  box-shadow:
    0 24px 56px rgba(83, 87, 71, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(18px);
}

.card-glow {
  position: absolute;
  top: 138px;
  left: 50%;
  transform: translateX(-50%);
  color: rgba(158, 131, 109, 0.24);
  font-size: clamp(72px, 11vw, 104px);
  font-style: italic;
  letter-spacing: 0.08em;
  pointer-events: none;
  user-select: none;
}

.hero-copy {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  text-align: center;
}

.hero-title {
  margin: 0;
  color: #241f1b;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: clamp(34px, 4vw, 48px);
  line-height: 1.18;
}

.hero-title--accent {
  color: #d84a2a;
}

.hero-divider {
  width: 70px;
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, #d9a73a, #f1d987);
}

.reward-pill {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  margin: 34px 0 30px;
  padding: 14px 22px;
  border-radius: 16px;
  border: 1px solid rgba(233, 191, 100, 0.72);
  background: rgba(255, 249, 237, 0.78);
  color: #71553f;
  font-size: 18px;
}

.reward-pill strong {
  color: #d84a2a;
  font-weight: 700;
}

.gift-icon {
  font-size: 22px;
}

.register-form {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-label {
  color: #3a2d27;
  font-size: 19px;
  font-weight: 500;
}

.input-shell {
  display: flex;
  align-items: center;
  height: 68px;
  border: 1px solid rgba(217, 198, 183, 0.95);
  border-radius: 0;
  background: rgba(255, 255, 255, 0.9);
  overflow: hidden;
  box-shadow: 0 8px 22px rgba(138, 124, 108, 0.08);
}

.field-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  color: #9f8a7d;
  font-size: 24px;
}

.input-shell input {
  flex: 1;
  height: 100%;
  border: 0;
  padding: 0 18px 0 0;
  background: transparent;
  color: #392f29;
  font-size: 18px;
  outline: none;
}

.input-shell input::placeholder {
  color: rgba(122, 107, 98, 0.5);
}

.code-row {
  display: grid;
  grid-template-columns: 1fr 182px;
  gap: 16px;
}

.secondary-button,
.primary-button {
  border: 0;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    opacity 0.2s ease;
}

.secondary-button {
  height: 68px;
  border-radius: 14px;
  background: linear-gradient(180deg, rgba(255, 240, 230, 0.92), rgba(255, 224, 210, 0.78));
  color: #4b756a;
  font-size: 24px;
  font-family: "Noto Serif SC", "Songti SC", serif;
  box-shadow: inset 0 0 0 1px rgba(182, 124, 96, 0.28);
}

.secondary-button:disabled,
.primary-button:disabled {
  opacity: 0.72;
  cursor: not-allowed;
  transform: none;
}

.agreement {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  color: #6f6057;
  font-size: 15px;
  line-height: 1.7;
}

.agreement input {
  width: 20px;
  height: 20px;
  margin-top: 2px;
  accent-color: #c54a2b;
}

.mock-tip,
.message {
  margin: 0;
  color: #8f5138;
  font-size: 14px;
}

.primary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  height: 74px;
  margin-top: 6px;
  border-radius: 14px;
  background: linear-gradient(135deg, #d84b2b, #cb3d20);
  color: #fffdf8;
  font-size: 30px;
  font-weight: 700;
  box-shadow: 0 18px 32px rgba(203, 61, 32, 0.28);
}

.primary-button:not(:disabled):hover,
.secondary-button:not(:disabled):hover {
  transform: translateY(-1px);
}

.sparkle {
  font-size: 28px;
}

.card-footer {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 30px;
  color: #4e4039;
  font-size: 18px;
}

.card-footer a {
  color: #d84a2a;
  font-weight: 600;
  text-decoration: none;
}

@media (max-width: 720px) {
  .register-shell {
    padding: 18px 14px;
  }

  .register-card {
    padding: 34px 22px 28px;
    border-radius: 22px;
  }

  .card-glow {
    top: 132px;
    font-size: 72px;
  }

  .reward-pill {
    margin: 24px 0 22px;
    padding: 12px 16px;
    font-size: 15px;
  }

  .field-label {
    font-size: 16px;
  }

  .input-shell,
  .secondary-button {
    height: 58px;
  }

  .input-shell input {
    font-size: 16px;
  }

  .field-icon {
    width: 48px;
    font-size: 20px;
  }

  .code-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .secondary-button {
    font-size: 20px;
  }

  .primary-button {
    height: 62px;
    font-size: 22px;
  }

  .card-footer {
    font-size: 16px;
  }
}
</style>
