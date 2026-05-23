<template>
  <div class="home-page">
    <section class="hero-section">
      <div class="hero-background">
        <img
          :src="homeHeroImage"
          alt="绘梦首页背景"
        />
      </div>
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <div class="hero-copy">
          <div class="brand-mark">绘梦</div>
          <h1>一键绘就你的专属国风角色</h1>
          <p>
            无需专业技巧，输入灵感文字，即刻获得电影感、古风感、仙侠感兼具的国风角色图像。
            让每一个人设、封面、头像与故事角色，都拥有值得收藏的东方美学形象。
          </p>
          <div class="hero-actions">
            <RouterLink class="primary-button" to="/workspace">立即开始创作</RouterLink>
            <a class="secondary-button" href="#inspirations">浏览灵感模板</a>
          </div>
          <div class="hero-stats">
            <div>
              <strong>10W+</strong>
              <span>创作灵感模板</span>
            </div>
            <div>
              <strong>24h</strong>
              <span>模型智能守护</span>
            </div>
            <div>
              <strong>国风向</strong>
              <span>角色视觉优化</span>
            </div>
          </div>
        </div>

        <div class="hero-panel">
          <div class="hero-panel-head">
            <span>风格精选</span>
            <small>热门创作路线</small>
          </div>
          <div class="hero-style-grid">
            <article v-for="item in featuredStyles" :key="item.id" class="hero-style-card">
              <img :src="item.cover" :alt="item.name" />
              <div class="hero-style-overlay"></div>
              <div class="hero-style-copy">
                <span>{{ item.verticalName }}</span>
                <strong>{{ item.name }}</strong>
              </div>
            </article>
          </div>
        </div>
      </div>
    </section>

    <section id="inspirations" class="content-section inspiration-section">
      <div class="section-heading center">
        <h2>入画灵感</h2>
        <p>精选情绪模板，一键开启你的国风角色叙事</p>
      </div>
      <div class="inspiration-layout">
        <article class="inspiration-large inspiration-carousel">
          <button
            class="inspiration-preset"
            type="button"
            @click="goPreset('style_xianxia', 'tpl_novel_heroine', '清冷月下女剑仙，白衣长剑，月光与飞雪，孤高清绝')"
          >
            <img
              :src="currentSwordImmortalImage"
              class="sword-immortal-image"
              alt="清冷月下女剑仙"
              data-testid="sword-immortal-image"
            />
            <div class="inspiration-overlay"></div>
            <div class="inspiration-copy">
              <span class="inspiration-tag">清冷 · 仙气</span>
              <h3>清冷月下女剑仙</h3>
              <p>孤月照剑，衣袂生风。适合小说女主、封面角色与仙侠梦女人设。</p>
            </div>
          </button>
          <div class="carousel-controls" aria-label="清冷月下女剑仙图片轮播">
            <button
              class="carousel-arrow"
              type="button"
              aria-label="上一张清冷月下女剑仙"
              @click="showPreviousSwordImmortal"
            >
              ‹
            </button>
            <span class="carousel-count">{{ swordImmortalIndex + 1 }} / {{ swordImmortalImages.length }}</span>
            <button
              class="carousel-arrow"
              type="button"
              aria-label="下一张清冷月下女剑仙"
              data-testid="sword-immortal-next"
              @click="showNextSwordImmortal"
            >
              ›
            </button>
          </div>
        </article>
        <div class="inspiration-side">
          <article class="inspiration-small inspiration-carousel">
            <button
              class="inspiration-preset"
              type="button"
              @click="goPreset('style_tang_dynasty', 'tpl_dreamgirl_portrait', '长安贵族千金，金色步摇，红色齐胸襦裙，华贵端庄')"
            >
              <img
                :src="currentChanganNobleImage"
                alt="长安贵族千金"
                data-testid="changan-noble-image"
              />
              <div class="inspiration-overlay"></div>
              <div class="inspiration-copy compact">
                <h3>长安贵族千金</h3>
                <p>盛世华彩，适合头像与人设首图</p>
              </div>
            </button>
            <div class="carousel-controls compact" aria-label="长安贵族千金图片轮播">
              <button
                class="carousel-arrow"
                type="button"
                aria-label="上一张长安贵族千金"
                @click="showPreviousChanganNoble"
              >
                ‹
              </button>
              <span class="carousel-count">{{ changanNobleIndex + 1 }} / {{ changanNobleImages.length }}</span>
              <button
                class="carousel-arrow"
                type="button"
                aria-label="下一张长安贵族千金"
                data-testid="changan-noble-next"
                @click="showNextChanganNoble"
              >
                ›
              </button>
            </div>
          </article>
          <button
            class="inspiration-small"
            type="button"
            @click="goPreset('style_cinematic', 'tpl_xiaohongshu_cover', '病娇红衣妖姬，暗夜回眸，红伞，强情绪电影感')"
          >
            <img
              :src="redDemonImage"
              alt="病娇红衣妖姬"
            />
            <div class="inspiration-overlay"></div>
            <div class="inspiration-copy compact">
              <h3>病娇红衣妖姬</h3>
              <p>强氛围封面感，适合小红书与话题传播</p>
            </div>
          </button>
        </div>
      </div>
    </section>

    <section class="content-section gallery-section">
      <div class="section-heading between">
        <div>
          <h2>墨染·万象画廊</h2>
          <p>探索用户创作的惊艳作品</p>
        </div>
        <RouterLink class="gallery-link" to="/works">查看全部</RouterLink>
      </div>
      <div class="gallery-grid">
        <article v-for="item in galleryItems" :key="item.title" class="gallery-card">
          <img :src="item.image" :alt="item.title" />
          <div class="gallery-hover">
            <span>{{ item.title }}</span>
          </div>
        </article>
      </div>
    </section>

    <section class="cta-section">
      <div class="cta-mark"></div>
      <h2>此刻，绘就你的东方美学奇迹</h2>
      <p>
        超过 1,000,000+ 个独特国风角色已在绘梦中诞生。加入我们，
        赋予你的想象以形象，赋予你的文字以灵魂。
      </p>
      <RouterLink class="cta-button" to="/workspace">立即开启创作之旅</RouterLink>
    </section>

    <footer class="home-footer">
      <div class="footer-brand">
        <strong>绘梦</strong>
        <p>专业的 AI 国风角色创作平台，让传统美学在数字时代焕发新生。</p>
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
import { computed, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";
import swordImmortalImage1 from "@/assets/女剑仙1.png";
import swordImmortalImage2 from "@/assets/女剑仙2.png";
import swordImmortalImage3 from "@/assets/女剑仙3.png";
import swordImmortalImage4 from "@/assets/女剑仙4.png";
import changanNobleImage1 from "@/assets/长安贵族千金1.png";
import changanNobleImage2 from "@/assets/长安贵族千金2.png";
import changanNobleImage3 from "@/assets/长安贵族千金3.png";
import changanNobleImage4 from "@/assets/长安贵族千金4.png";
import galleryAutumnLakeImage from "@/assets/home-gallery-autumn-lake.jpg";
import galleryCinnabarRobeImage from "@/assets/home-gallery-cinnabar-robe.jpg";
import galleryFlowerShadowImage from "@/assets/home-gallery-flower-shadow.jpg";
import galleryGoldenButterflyImage from "@/assets/home-gallery-golden-butterfly.jpg";
import galleryMoonSwordImage from "@/assets/home-gallery-moon-sword.jpg";
import homeHeroImage from "@/assets/home-hero-guofeng-studio.jpg";
import redDemonImage from "@/assets/home-template-red-demon.jpg";
import styleCinematicImage from "@/assets/home-style-cinematic.jpg";
import styleGufengPortraitImage from "@/assets/home-style-gufeng-portrait.jpg";
import styleHanDynastyImage from "@/assets/home-style-han-dynasty.jpg";
import styleNewChineseImage from "@/assets/home-style-new-chinese.jpg";
import styleTangDynastyImage from "@/assets/home-style-tang-dynasty.jpg";
import styleXianxiaImage from "@/assets/home-style-xianxia.jpg";
import { styles } from "@/shared/catalog";

const router = useRouter();
const swordImmortalImages = [
  swordImmortalImage1,
  swordImmortalImage2,
  swordImmortalImage3,
  swordImmortalImage4,
];
const changanNobleImages = [
  changanNobleImage1,
  changanNobleImage2,
  changanNobleImage3,
  changanNobleImage4,
];
const swordImmortalIndex = ref(0);
const changanNobleIndex = ref(0);
const currentSwordImmortalImage = computed(() => swordImmortalImages[swordImmortalIndex.value]);
const currentChanganNobleImage = computed(() => changanNobleImages[changanNobleIndex.value]);

const featuredStyles = computed(() => {
  const coverMap: Record<string, { cover: string; verticalName: string }> = {
    style_tang_dynasty: {
      cover: styleTangDynastyImage,
      verticalName: "盛唐气象",
    },
    style_han_dynasty: {
      cover: styleHanDynastyImage,
      verticalName: "清汉古韵",
    },
    style_xianxia: {
      cover: styleXianxiaImage,
      verticalName: "仙侠梦境",
    },
    style_new_chinese: {
      cover: styleNewChineseImage,
      verticalName: "新中式质感",
    },
    style_gufeng_portrait: {
      cover: styleGufengPortraitImage,
      verticalName: "古风肖像",
    },
    style_cinematic: {
      cover: styleCinematicImage,
      verticalName: "电影镜头",
    },
  };

  return styles.slice(0, 4).map((style) => ({
    ...style,
    cover: coverMap[style.id]?.cover ?? coverMap.style_tang_dynasty.cover,
    verticalName: coverMap[style.id]?.verticalName ?? "东方美学",
  }));
});

const galleryItems = [
  {
    title: "月下剑影",
    image: galleryMoonSwordImage,
  },
  {
    title: "朱砂华裳",
    image: galleryCinnabarRobeImage,
  },
  {
    title: "金阙蝶梦",
    image: galleryGoldenButterflyImage,
  },
  {
    title: "花钿弄影",
    image: galleryFlowerShadowImage,
  },
  {
    title: "平湖秋月",
    image: galleryAutumnLakeImage,
  },
];

function previousIndex(currentIndex: number, total: number) {
  return (currentIndex - 1 + total) % total;
}

function nextIndex(currentIndex: number, total: number) {
  return (currentIndex + 1) % total;
}

function showPreviousSwordImmortal() {
  swordImmortalIndex.value = previousIndex(swordImmortalIndex.value, swordImmortalImages.length);
}

function showNextSwordImmortal() {
  swordImmortalIndex.value = nextIndex(swordImmortalIndex.value, swordImmortalImages.length);
}

function showPreviousChanganNoble() {
  changanNobleIndex.value = previousIndex(changanNobleIndex.value, changanNobleImages.length);
}

function showNextChanganNoble() {
  changanNobleIndex.value = nextIndex(changanNobleIndex.value, changanNobleImages.length);
}

function goPreset(styleId: string, templateId?: string, prompt?: string) {
  router.push({
    name: "workspace",
    query: {
      style: styleId,
      template: templateId,
      prompt,
    },
  });
}
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: 72px;
  padding-bottom: 72px;
  color: #171717;
}

.hero-section {
  position: relative;
  min-height: 820px;
  overflow: hidden;
  margin-inline: calc(50% - 50vw);
}

.hero-background,
.hero-background img,
.hero-overlay {
  position: absolute;
  inset: 0;
}

.hero-background img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  background:
    linear-gradient(90deg, rgba(247, 243, 239, 0.94) 0%, rgba(247, 243, 239, 0.72) 28%, rgba(247, 243, 239, 0.14) 58%, rgba(247, 243, 239, 0.04) 100%),
    linear-gradient(180deg, rgba(17, 17, 17, 0.06), rgba(17, 17, 17, 0.12));
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 48px;
  width: min(1200px, calc(100% - 80px));
  margin: 0 auto;
  padding: 120px 0 96px;
}

.hero-copy {
  max-width: 560px;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 68px;
  padding: 10px 16px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.68);
  color: #7a4730;
  font-size: 14px;
  letter-spacing: 0.24em;
}

.hero-copy h1 {
  margin: 24px 0 18px;
  color: #1b1715;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: clamp(44px, 7vw, 72px);
  line-height: 1.06;
}

.hero-copy p {
  margin: 0;
  max-width: 520px;
  color: rgba(44, 35, 31, 0.8);
  font-size: 18px;
  line-height: 1.9;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 32px;
}

.primary-button,
.secondary-button,
.cta-button,
.gallery-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.primary-button,
.cta-button {
  min-height: 54px;
  padding: 0 28px;
  border-radius: 999px;
  background: linear-gradient(135deg, #ad5531, #cc7a47);
  color: #fff9f1;
  box-shadow: 0 16px 32px rgba(167, 90, 53, 0.22);
}

.secondary-button {
  min-height: 54px;
  padding: 0 28px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  color: #5c4338;
  border: 1px solid rgba(182, 139, 116, 0.28);
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 36px;
}

.hero-stats div {
  padding: 18px 16px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(8px);
}

.hero-stats strong {
  display: block;
  margin-bottom: 8px;
  color: #7d4026;
  font-size: 28px;
}

.hero-stats span {
  color: rgba(56, 41, 34, 0.7);
  font-size: 14px;
}

.hero-panel {
  width: min(420px, 100%);
  padding: 24px;
  border-radius: 36px;
  background: rgba(255, 252, 248, 0.72);
  backdrop-filter: blur(12px);
  box-shadow: 0 28px 80px rgba(52, 37, 28, 0.18);
}

.hero-panel-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 20px;
  color: #52382d;
}

.hero-panel-head span {
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 22px;
}

.hero-panel-head small {
  color: rgba(82, 56, 45, 0.58);
}

.hero-style-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.hero-style-card {
  position: relative;
  aspect-ratio: 0.78;
  overflow: hidden;
  border-radius: 24px;
}

.hero-style-card img,
.gallery-card img,
.inspiration-large img,
.inspiration-small img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.inspiration-carousel .inspiration-preset img {
  object-fit: cover;
}

.sword-immortal-image {
  object-position: center top;
}

.hero-style-overlay,
.gallery-hover,
.inspiration-overlay {
  position: absolute;
  inset: 0;
}

.hero-style-overlay {
  background: linear-gradient(180deg, rgba(10, 10, 10, 0.02), rgba(10, 10, 10, 0.72));
}

.hero-style-copy {
  position: absolute;
  left: 14px;
  right: 14px;
  bottom: 14px;
  color: #fff;
}

.hero-style-copy span {
  font-size: 12px;
  letter-spacing: 0.16em;
}

.hero-style-copy strong {
  display: block;
  margin-top: 8px;
  font-size: 22px;
}

.content-section {
  width: min(1200px, calc(100% - 64px));
  margin: 0 auto;
}

.section-heading {
  display: flex;
  gap: 16px;
  margin-bottom: 28px;
}

.section-heading.center {
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.section-heading.between {
  align-items: flex-end;
  justify-content: space-between;
}

.section-heading h2 {
  margin: 0;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: clamp(30px, 4vw, 42px);
}

.section-heading p {
  margin: 0;
  color: rgba(72, 56, 48, 0.7);
  font-size: 16px;
}

.inspiration-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(360px, 0.95fr);
  gap: 22px;
  align-items: stretch;
}

.inspiration-large,
.inspiration-small {
  position: relative;
  overflow: hidden;
  border: 0;
  padding: 0;
  border-radius: 30px;
  background: #f4ebe3;
}

.inspiration-preset {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: 0;
  padding: 0;
  cursor: pointer;
  background: transparent;
}

.inspiration-large {
  min-height: 900px;
}

.inspiration-side {
  display: grid;
  gap: 22px;
}

.inspiration-small {
  min-height: 369px;
}

.carousel-controls {
  position: absolute;
  z-index: 2;
  top: 24px;
  right: 24px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 999px;
  background: rgba(18, 14, 12, 0.48);
  backdrop-filter: blur(10px);
}

.carousel-controls.compact {
  top: 18px;
  right: 18px;
  padding: 6px;
}

.carousel-arrow {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid rgba(255, 247, 242, 0.28);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
  color: #fff8f2;
  cursor: pointer;
  font-size: 26px;
  line-height: 1;
  transition:
    background 0.2s ease,
    transform 0.2s ease;
}

.carousel-controls.compact .carousel-arrow {
  width: 30px;
  height: 30px;
  font-size: 22px;
}

.carousel-arrow:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.carousel-count {
  min-width: 44px;
  color: rgba(255, 248, 243, 0.88);
  font-size: 13px;
  text-align: center;
}

.inspiration-overlay {
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.04), rgba(0, 0, 0, 0.7));
}

.inspiration-copy {
  position: absolute;
  left: 28px;
  right: 28px;
  bottom: 30px;
  color: #fff7f2;
  text-align: left;
}

.inspiration-copy.compact {
  left: 22px;
  right: 22px;
  bottom: 22px;
}

.inspiration-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  font-size: 13px;
  letter-spacing: 0.16em;
}

.inspiration-copy h3 {
  margin: 16px 0 10px;
  font-size: clamp(32px, 4vw, 46px);
  font-family: "Noto Serif SC", "Songti SC", serif;
}

.inspiration-copy.compact h3 {
  margin: 0 0 8px;
  font-size: 28px;
}

.inspiration-copy p {
  max-width: 520px;
  margin: 0;
  color: rgba(255, 248, 243, 0.88);
  font-size: 16px;
  line-height: 1.8;
}

.gallery-link {
  min-height: 48px;
  padding: 0 20px;
  border-radius: 999px;
  background: rgba(237, 222, 206, 0.56);
  color: #714934;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 18px;
}

.gallery-card {
  position: relative;
  aspect-ratio: 0.74;
  overflow: hidden;
  border-radius: 28px;
  background: #f5eee7;
}

.gallery-hover {
  display: flex;
  align-items: flex-end;
  padding: 18px;
  background: linear-gradient(180deg, rgba(14, 12, 11, 0.02), rgba(14, 12, 11, 0.68));
  color: #fff5ef;
}

.cta-section {
  position: relative;
  width: min(1120px, calc(100% - 64px));
  margin: 0 auto;
  padding: 64px 72px;
  border-radius: 40px;
  overflow: hidden;
  background: linear-gradient(135deg, #fff7ef, #f5e6d6);
  text-align: center;
  box-shadow: 0 18px 48px rgba(61, 43, 30, 0.08);
}

.cta-mark {
  position: absolute;
  inset: auto auto -80px -40px;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(216, 163, 104, 0.2), transparent 70%);
}

.cta-section h2 {
  margin: 0;
  font-size: clamp(32px, 4vw, 46px);
  font-family: "Noto Serif SC", "Songti SC", serif;
}

.cta-section p {
  max-width: 760px;
  margin: 18px auto 32px;
  color: rgba(71, 52, 41, 0.74);
  font-size: 17px;
  line-height: 1.9;
}

.home-footer {
  width: min(1200px, calc(100% - 64px));
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding-bottom: 12px;
  color: rgba(66, 47, 40, 0.7);
}

.footer-brand strong {
  display: block;
  margin-bottom: 10px;
  color: #3a241b;
  font-size: 18px;
}

.footer-brand p {
  max-width: 420px;
  margin: 0;
  line-height: 1.8;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  align-content: flex-start;
}

.footer-links a {
  color: inherit;
  text-decoration: none;
}

@media (max-width: 1080px) {
  .hero-content,
  .home-footer {
    width: min(100%, calc(100% - 48px));
  }

  .hero-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-panel {
    width: 100%;
  }

  .gallery-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 860px) {
  .inspiration-layout {
    grid-template-columns: 1fr;
  }

  .inspiration-large,
  .inspiration-small {
    min-height: 340px;
  }

  .hero-stats {
    grid-template-columns: 1fr;
  }

  .gallery-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .home-footer,
  .section-heading.between {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .hero-content {
    width: min(100%, calc(100% - 32px));
    padding: 88px 0 72px;
  }

  .content-section,
  .home-footer,
  .cta-section {
    width: min(100%, calc(100% - 32px));
  }

  .cta-section {
    padding: 42px 24px;
  }

  .gallery-grid,
  .hero-style-grid {
    grid-template-columns: 1fr;
  }
}
</style>
