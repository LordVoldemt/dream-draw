<template>
  <div class="generating-page">
    <div class="page-background"></div>
    <div class="page-overlay"></div>

    <div class="vertical-brand">墨染梦境</div>

    <section class="generating-shell">
      <div class="art-ring">
        <div class="art-ring-track"></div>
        <div class="art-ring-progress" :style="{ '--progress': `${progress}%` }"></div>
        <div class="art-core">
          <img
            src="https://images.unsplash.com/photo-1516490981167-dc990a242afe?auto=format&fit=crop&w=700&q=80"
            alt="墨染意象"
          />
        </div>
      </div>

      <h1>AI 正在墨染梦境中…</h1>

      <div class="eta-row">
        <span class="eta-icon">◔</span>
        <span>{{ statusText }}</span>
      </div>

      <div class="progress-bar">
        <span :style="{ width: `${progress}%` }"></span>
      </div>

      <article class="tip-card">
        <div class="tip-icon">💡</div>
        <div class="tip-copy">
          <strong>创作贴士（CREATIVE TIP）</strong>
          <p>试试在提示词中加入“烟雨朦胧”或“朱砂点缀”，这能让生成的画面更具中国画的韵律美。</p>
        </div>
      </article>

      <div v-if="errorMessage" class="error-card">
        <p>{{ errorMessage }}</p>
        <div class="error-actions">
          <button type="button" class="secondary-action" @click="goWorkspace">返回重试</button>
          <button type="button" class="primary-action" @click="pollTask">重新检查</button>
        </div>
      </div>

      <p class="copyright">© 2024 墨染梦境 Ink Dream AI. All Rights Reserved.</p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
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

const progress = ref(24);
const errorMessage = ref("");
const taskStatus = ref("pending");
const taskId = computed(() => Number(route.query.taskId || route.params.id || 0));
let progressTimer: number | null = null;
let pollTimer: number | null = null;

const statusText = computed(() => {
  if (errorMessage.value) {
    return errorMessage.value;
  }
  if (taskStatus.value === "reviewing") {
    return "作品即将完成，正在做最后润色与审核";
  }
  if (taskStatus.value === "generating") {
    return "正在生成画面，预计还需数分钟";
  }
  return "作品已提交，正在排队进入绘制流程";
});

function stopTimers() {
  if (progressTimer !== null) {
    window.clearInterval(progressTimer);
    progressTimer = null;
  }
  if (pollTimer !== null) {
    window.clearInterval(pollTimer);
    pollTimer = null;
  }
}

async function handleSuccess(taskIdValue: number) {
  stopTimers();
  const workResponse = await api.getWorkDetailByTask(taskIdValue);
  await router.replace(`/result/${String(workResponse.work.id ?? taskIdValue)}`);
}

async function pollTask() {
  if (!taskId.value) {
    errorMessage.value = "缺少任务编号，请返回重新生成。";
    stopTimers();
    return;
  }
  try {
    const response = await api.getTaskDetail(taskId.value);
    taskStatus.value = String(response.task.status ?? "pending");
    if (taskStatus.value === "success") {
      progress.value = 100;
      await handleSuccess(taskId.value);
      return;
    }
    if (taskStatus.value === "failed") {
      errorMessage.value = "生成失败，积分已自动退回，请调整描述或稍后重试。";
      stopTimers();
      return;
    }
    if (taskStatus.value === "blocked") {
      errorMessage.value = "作品未通过审核，积分已自动退回。";
      stopTimers();
      return;
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "查询生成状态失败，请稍后重试。";
    stopTimers();
  }
}

async function goWorkspace() {
  await router.push({ name: "workspace" });
}

onMounted(() => {
  progressTimer = window.setInterval(() => {
    progress.value = Math.min(96, progress.value + 8);
  }, 1000);
  void pollTask();
  pollTimer = window.setInterval(() => {
    void pollTask();
  }, 3000);
});

onBeforeUnmount(() => {
  stopTimers();
});
</script>

<style scoped>
.generating-page {
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
    linear-gradient(180deg, rgba(245, 240, 232, 0.76), rgba(245, 240, 232, 0.78)),
    repeating-linear-gradient(
      120deg,
      rgba(246, 232, 214, 0.52) 0,
      rgba(246, 232, 214, 0.52) 90px,
      rgba(230, 236, 239, 0.5) 90px,
      rgba(230, 236, 239, 0.5) 180px
    );
}

.page-overlay {
  background:
    radial-gradient(circle at top center, rgba(255, 246, 221, 0.75), transparent 36%),
    linear-gradient(180deg, rgba(255, 252, 246, 0.2), rgba(223, 231, 233, 0.16));
}

.vertical-brand {
  position: absolute;
  top: 28px;
  right: 34px;
  z-index: 1;
  padding: 10px 8px;
  border: 1px solid rgba(223, 142, 123, 0.75);
  color: rgba(225, 131, 111, 0.9);
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 18px;
  line-height: 1.35;
  writing-mode: vertical-rl;
  text-orientation: mixed;
}

.generating-shell {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 64px 20px 32px;
}

.art-ring {
  position: relative;
  width: 342px;
  height: 342px;
  margin-bottom: 34px;
}

.art-ring-track,
.art-ring-progress {
  position: absolute;
  inset: 0;
  border-radius: 50%;
}

.art-ring-track {
  border: 2px solid rgba(221, 196, 145, 0.44);
}

.art-ring-progress {
  background: conic-gradient(#d5a018 0turn, #d5a018 calc(var(--progress) / 100 * 1turn), transparent 0turn);
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 3px), #000 calc(100% - 2px));
  mask: radial-gradient(farthest-side, transparent calc(100% - 3px), #000 calc(100% - 2px));
}

.art-core {
  position: absolute;
  inset: 50px;
  border-radius: 50%;
  overflow: hidden;
  box-shadow:
    0 0 0 12px rgba(255, 249, 239, 0.44),
    0 20px 45px rgba(110, 105, 92, 0.12);
}

.art-core img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.generating-shell h1 {
  margin: 0;
  color: #151515;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 54px;
  line-height: 1.2;
  font-weight: 700;
}

.eta-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 18px;
  color: #5e4037;
  font-size: 18px;
}

.eta-icon {
  display: inline-grid;
  place-items: center;
  width: 24px;
  height: 24px;
  font-size: 18px;
}

.progress-bar {
  width: min(560px, calc(100vw - 80px));
  height: 6px;
  margin-top: 82px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.progress-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #df3a23, #f04a28);
  box-shadow: 0 2px 8px rgba(224, 64, 33, 0.22);
}

.tip-card,
.error-card {
  width: min(600px, calc(100vw - 48px));
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(255, 255, 255, 0.64);
  box-shadow: 0 24px 48px rgba(114, 117, 111, 0.1);
  backdrop-filter: blur(14px);
}

.tip-card {
  display: grid;
  grid-template-columns: 54px 1fr;
  gap: 18px;
  margin-top: 138px;
  padding: 28px 30px;
}

.tip-icon {
  display: grid;
  place-items: center;
  width: 54px;
  height: 54px;
  border-radius: 12px;
  background: rgba(82, 129, 113, 0.12);
  font-size: 24px;
}

.tip-copy strong {
  display: block;
  color: #4c8372;
  font-size: 18px;
  margin-bottom: 8px;
}

.tip-copy p {
  margin: 0;
  color: #4f4039;
  font-size: 16px;
  line-height: 1.85;
}

.error-card {
  margin-top: 24px;
  padding: 24px 28px;
  color: #7b3827;
}

.error-card p {
  margin: 0;
  line-height: 1.8;
}

.error-actions {
  display: flex;
  gap: 12px;
  margin-top: 18px;
}

.primary-action,
.secondary-action {
  height: 44px;
  padding: 0 20px;
  border-radius: 999px;
  font-size: 15px;
  cursor: pointer;
}

.primary-action {
  border: 0;
  background: linear-gradient(135deg, #d53a25, #f05a2b);
  color: #fff;
}

.secondary-action {
  border: 1px solid rgba(190, 156, 142, 0.56);
  background: rgba(255, 255, 255, 0.8);
  color: #5a4036;
}

.copyright {
  margin: 10px 0 0;
  color: rgba(68, 68, 68, 0.38);
  font-size: 14px;
}

@media (max-width: 720px) {
  .vertical-brand {
    top: 20px;
    right: 20px;
  }

  .art-ring {
    width: 272px;
    height: 272px;
    margin-bottom: 28px;
  }

  .art-core {
    inset: 40px;
  }

  .generating-shell h1 {
    font-size: 34px;
    text-align: center;
  }

  .eta-row {
    font-size: 16px;
  }

  .progress-bar {
    margin-top: 54px;
  }

  .tip-card {
    grid-template-columns: 1fr;
    margin-top: 72px;
    padding: 24px;
  }

  .error-actions {
    flex-direction: column;
  }
}
</style>
