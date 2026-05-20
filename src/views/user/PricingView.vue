<template>
  <div class="pricing-page">
    <section class="hero-card">
      <div>
        <h1>算力点数中心</h1>
        <p>为您开启无限艺术创作之门</p>
      </div>
      <div class="balance-panel">
        <span class="balance-label">当前余额</span>
        <strong>{{ session.pointsBalance ?? 0 }}</strong>
      </div>
    </section>

    <section class="content-grid">
      <div class="left-column">
        <article class="side-card">
          <h2>点数使用规则</h2>
          <ul class="rule-list">
            <li v-for="item in rules" :key="item.name">
              <span>{{ item.name }}</span>
              <strong>{{ item.cost }}</strong>
            </li>
          </ul>
        </article>

        <article class="side-card benefit-card">
          <h2>尊享权益</h2>
          <div class="benefit-list">
            <div v-for="item in benefits" :key="item.title" class="benefit-item">
              <strong>{{ item.title }}</strong>
              <p>{{ item.text }}</p>
            </div>
          </div>
        </article>
      </div>

      <div class="main-column">
        <section class="section-block">
          <h2>选择充值包</h2>
          <div class="package-grid">
            <article
              v-for="pkg in packages"
              :key="pkg.id"
              class="package-card"
              :class="{ active: selectedPackageId === pkg.id, featured: pkg.id === 'pkg_100' }"
              @click="selectedPackageId = pkg.id"
            >
              <span v-if="pkg.id === 'pkg_100'" class="badge">最受欢迎</span>
              <p class="package-tag">{{ pkg.tag }}</p>
              <strong>{{ pkg.points }}</strong>
              <span class="unit">点</span>
              <p class="price">￥{{ pkg.price }}</p>
              <button class="select-button" type="button">选择</button>
            </article>
          </div>
        </section>

        <section class="section-block">
          <h2>支付方式</h2>
          <div class="channel-row">
            <button
              v-for="channel in channels"
              :key="channel.id"
              type="button"
              class="channel"
              :class="{ active: selectedChannel === channel.id }"
              @click="selectedChannel = channel.id"
            >
              <span class="channel-icon">{{ channel.icon }}</span>
              <span class="channel-label">{{ channel.label }}</span>
              <span class="channel-radio"></span>
            </button>
          </div>
        </section>

        <div class="submit-wrap">
          <button class="submit" type="button" @click="createOrder">立即充值</button>
          <p class="agreement">
            点击充值即代表您已同意<a href="#">充值协议</a>
          </p>
          <p v-if="message" class="message">{{ message }}</p>
        </div>
      </div>
    </section>

    <footer class="page-footer">
      <div class="footer-brand">
        <strong>墨染梦境</strong>
        <p>© 2024 墨染梦境 Ink Dream AI. All Rights Reserved.</p>
      </div>
      <div class="footer-links">
        <a href="#">关于我们</a>
        <a href="#">使用协议</a>
        <a href="#">隐私政策</a>
        <a href="#">联系支持</a>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { ApiClient } from "@/api/client";
import { DreamDrawApi } from "@/api/dream-draw";
import { useSessionStore } from "@/stores/session";

const session = useSessionStore();
const api = new DreamDrawApi(
  new ApiClient({
    getToken: () => session.userToken,
  }),
);

const packages = [
  { id: "pkg_30", points: 30, price: 9.9, tag: "入门体验" },
  { id: "pkg_100", points: 100, price: 29.9, tag: "高性价比" },
  { id: "pkg_300", points: 300, price: 69.9, tag: "专业创作" },
];

const channels = [
  { id: "wechat" as const, label: "微信支付", icon: "￥" },
  { id: "alipay" as const, label: "支付宝", icon: "支" },
];

const rules = [
  { name: "标准生成", cost: "1 pt / 张" },
  { name: "HD 高清生成", cost: "2 pt / 张" },
  { name: "RAW 原始精度", cost: "5 pt / 张" },
  { name: "风格自定义训练", cost: "20 pt / 次" },
];

const benefits = [
  { title: "极速优先生成", text: "高峰时段无需排队，独立渲染通道。" },
  { title: "专属风格模板", text: "解锁大师级独家“仙侠”与“墨染”预设。" },
];

const selectedPackageId = ref("pkg_100");
const selectedChannel = ref<"wechat" | "alipay">("wechat");
const message = ref("");

async function createOrder() {
  try {
    const response = await api.createPaymentOrder({
      package_id: selectedPackageId.value,
      channel: selectedChannel.value,
    });
    message.value = `订单已创建，订单号：${response.order.id}`;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "创建订单失败";
  }
}
</script>

<style scoped>
.pricing-page {
  display: flex;
  flex-direction: column;
  gap: 44px;
  padding-bottom: 28px;
}

.hero-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  min-height: 216px;
  padding: 0 60px;
  border-radius: 28px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(252, 252, 252, 0.9));
  box-shadow: 0 18px 42px rgba(43, 39, 35, 0.06);
}

.hero-card h1,
.section-block h2,
.side-card h2 {
  margin: 0;
  color: #171717;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 36px;
  line-height: 1.2;
}

.hero-card p {
  margin: 16px 0 0;
  color: #5f463b;
  font-size: 16px;
}

.balance-panel {
  text-align: right;
}

.balance-label {
  display: inline-block;
  margin-bottom: 10px;
  color: #497568;
  font-size: 16px;
}

.balance-panel strong {
  display: block;
  color: #d64627;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 66px;
  line-height: 1;
}

.content-grid {
  display: grid;
  grid-template-columns: 460px minmax(0, 1fr);
  gap: 40px;
}

.left-column,
.main-column {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.side-card {
  padding: 34px 30px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 14px 34px rgba(46, 42, 37, 0.06);
}

.rule-list,
.benefit-list {
  display: flex;
  flex-direction: column;
  gap: 22px;
  margin: 26px 0 0;
  padding: 0;
  list-style: none;
}

.rule-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  color: #362b27;
  font-size: 17px;
}

.rule-list strong {
  color: #4f4039;
  font-weight: 500;
}

.benefit-card {
  background: linear-gradient(180deg, #f8fbf8, #f2f5f1);
}

.benefit-card h2 {
  color: #4f7f71;
}

.benefit-item strong {
  display: block;
  margin-bottom: 8px;
  color: #171717;
  font-size: 18px;
}

.benefit-item p {
  margin: 0;
  color: #64534a;
  line-height: 1.75;
}

.section-block {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.package-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 28px;
}

.package-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 276px;
  padding: 32px 22px 24px;
  border: 1px solid rgba(218, 205, 194, 0.9);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 14px 30px rgba(41, 37, 33, 0.04);
  cursor: pointer;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.package-card:hover {
  transform: translateY(-4px);
}

.package-card.active {
  border-color: #d1a21c;
  box-shadow: 0 18px 36px rgba(209, 162, 28, 0.08);
}

.package-card.featured {
  border-width: 2px;
}

.badge {
  position: absolute;
  top: -14px;
  padding: 6px 18px;
  border-radius: 999px;
  background: #d7a822;
  color: #fff;
  font-size: 14px;
}

.package-tag {
  margin: 8px 0 24px;
  color: #bb4430;
  font-size: 18px;
}

.package-card strong {
  color: #171717;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 54px;
  line-height: 1;
  font-weight: 600;
}

.unit {
  margin-top: 6px;
  color: #302522;
  font-size: 18px;
}

.price {
  margin: 14px 0 30px;
  color: #523930;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 28px;
}

.select-button {
  width: 100%;
  height: 48px;
  border: 1px solid rgba(218, 106, 82, 0.45);
  border-radius: 12px;
  background: #fff;
  color: #2b221f;
  font-size: 16px;
}

.package-card.active .select-button {
  border-color: #d24d30;
  background: #d24d30;
  color: #fff;
}

.channel-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22px;
}

.channel {
  display: grid;
  grid-template-columns: 40px 1fr 22px;
  align-items: center;
  gap: 16px;
  height: 74px;
  padding: 0 22px;
  border: 1px solid rgba(224, 201, 189, 0.9);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.96);
  color: #251d1a;
  cursor: pointer;
}

.channel.active {
  border-color: #4f8973;
  box-shadow: inset 0 0 0 1px #4f8973;
}

.channel-icon {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(79, 137, 115, 0.1);
  color: #21b35d;
  font-weight: 700;
}

.channel:last-child .channel-icon {
  background: rgba(54, 120, 255, 0.08);
  color: #2e6bff;
}

.channel-label {
  justify-self: start;
  font-size: 17px;
}

.channel-radio {
  width: 18px;
  height: 18px;
  border: 1.5px solid rgba(92, 88, 84, 0.7);
  border-radius: 50%;
}

.channel.active .channel-radio {
  border-width: 6px;
  border-color: #4f8973;
}

.submit-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 18px;
}

.submit {
  width: min(360px, 100%);
  height: 80px;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, #d04e31, #c54124);
  color: #fff;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 28px;
  cursor: pointer;
  box-shadow: 0 18px 32px rgba(198, 65, 36, 0.18);
}

.agreement,
.message {
  margin: 18px 0 0;
  color: #6a574d;
  font-size: 14px;
}

.agreement a {
  color: #7f3f2c;
  text-decoration: underline;
}

.page-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 24px;
  padding-top: 54px;
  border-top: 1px solid rgba(208, 191, 181, 0.34);
}

.footer-brand strong {
  display: block;
  margin-bottom: 12px;
  color: rgba(27, 27, 27, 0.24);
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 52px;
}

.footer-brand p {
  margin: 0;
  color: #3c312d;
  font-size: 13px;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  gap: 48px;
}

.footer-links a {
  color: #251d1a;
  text-decoration: none;
  font-size: 16px;
}

@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .hero-card {
    flex-direction: column;
    align-items: flex-start;
    padding: 36px 28px;
  }

  .balance-panel {
    text-align: left;
  }

  .package-grid,
  .channel-row {
    grid-template-columns: 1fr;
  }

  .page-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .footer-links {
    gap: 20px;
  }
}
</style>
