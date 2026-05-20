<template>
  <div class="reward-page">
    <section class="reward-card">
      <span class="eyebrow">首登开户奖励</span>
      <h1>欢迎来到绘梦</h1>
      <p>你的账号已自动开通，并获得 <strong>10 积分</strong> 的新手体验额度。</p>
      <div class="reward-panel">
        <div>
          <span>当前手机号</span>
          <strong>{{ session.phone ?? "-" }}</strong>
        </div>
        <div>
          <span>当前积分</span>
          <strong>{{ session.pointsBalance ?? 0 }}</strong>
        </div>
      </div>
      <RouterLink class="primary" to="/workspace">返回生成流程</RouterLink>
    </section>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";
import { useSessionStore } from "@/stores/session";

const session = useSessionStore();
</script>

<style scoped>
.reward-page {
  display: grid;
  place-items: center;
  min-height: calc(100vh - 180px);
}

.reward-card {
  width: min(760px, 100%);
  padding: 40px;
  border-radius: 36px;
  text-align: center;
  background: linear-gradient(135deg, #fff8f1, #f7ead8);
  border: 1px solid rgba(128, 76, 36, 0.12);
}

.eyebrow {
  color: #bb6730;
  letter-spacing: 0.14em;
  font-size: 13px;
}

.reward-card h1 {
  margin: 14px 0 10px;
  color: #5b2d18;
  font-size: 44px;
}

.reward-card p {
  color: #725949;
  line-height: 1.8;
}

.reward-panel {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin: 26px 0;
}

.reward-panel div {
  padding: 18px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.75);
}

.reward-panel span {
  display: block;
  margin-bottom: 8px;
  color: #846553;
}

.reward-panel strong {
  color: #6d3c1f;
  font-size: 28px;
}

.primary {
  display: inline-flex;
  border-radius: 999px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #b14d1f, #d78536);
  color: #fff;
  text-decoration: none;
}
</style>
