<template>
  <div class="home-page">
    <section class="hero-section">
      <div class="hero-background">
        <img
          src="https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=1600&q=80"
          alt="国风角色主视觉"
        />
        <div class="hero-overlay"></div>
      </div>
      <div class="hero-content">
        <div class="hero-copy">
          <p class="hero-kicker">专注女性向国风 OC / 梦女人设生成</p>
          <h1>
            输入一句描述，
            <br />
            生成你的<span>专属国风</span>角色
          </h1>
          <p class="hero-description">
            融合东方意境与现代 AI，让一个梦境中的绝代佳人跃然纸上。
            从长安贵族到仙山剑仙，开始你的中式幻想之旅。
          </p>
          <div class="hero-actions">
            <RouterLink class="primary-button" to="/workspace">立即生成</RouterLink>
            <a class="secondary-button" href="#inspirations">探索灵感</a>
          </div>
        </div>
      </div>
    </section>

    <section class="content-section">
      <div class="section-title with-line">
        <span></span>
        <h2>格律传承 · 四大风格</h2>
      </div>
      <div class="style-grid">
        <button
          v-for="style in featuredStyles"
          :key="style.id"
          class="style-card"
          type="button"
          @click="goPreset(style.id)"
        >
          <img :src="style.cover" :alt="style.name" />
          <div class="style-card-overlay"></div>
          <div class="style-card-label">
            <span>{{ style.verticalName }}</span>
          </div>
        </button>
      </div>
    </section>

    <section id="inspirations" class="content-section inspiration-section">
      <div class="section-heading center">
        <h2>入画灵感</h2>
        <p>精选情绪模板，一键开启你的国风角色叙事</p>
      </div>
      <div class="inspiration-layout">
        <button
          class="inspiration-large"
          type="button"
          @click="goPreset('style_xianxia', 'tpl_novel_heroine', '清冷月下女剑仙，白衣长剑，月光与飞雪，孤高清绝')"
        >
          <img
            src="https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=1200&q=80"
            alt="清冷月下女剑仙"
          />
          <div class="inspiration-overlay"></div>
          <div class="inspiration-copy">
            <span class="inspiration-tag">清冷 · 仙气</span>
            <h3>清冷月下女剑仙</h3>
            <p>孤月照剑，衣袂生风。适合小说女主、封面角色与仙侠梦女人设。</p>
          </div>
        </button>
        <div class="inspiration-side">
          <button
            class="inspiration-small"
            type="button"
            @click="goPreset('style_tang_dynasty', 'tpl_dreamgirl_portrait', '长安贵族千金，金色步摇，红色齐胸襦裙，华贵端庄')"
          >
            <img
              src="https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=900&q=80"
              alt="长安贵族千金"
            />
            <div class="inspiration-overlay"></div>
            <div class="inspiration-copy compact">
              <h3>长安贵族千金</h3>
              <p>盛世华彩，适合头像与人设首图</p>
            </div>
          </button>
          <button
            class="inspiration-small"
            type="button"
            @click="goPreset('style_cinematic', 'tpl_xiaohongshu_cover', '病娇红衣妖姬，暗夜回眸，红伞，强情绪电影感')"
          >
            <img
              src="https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=900&q=80"
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
        <strong>墨染梦境</strong>
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
import { computed } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { styles } from "@/shared/catalog";

const router = useRouter();

const featuredStyles = computed(() => {
  const coverMap: Record<string, { cover: string; verticalName: string }> = {
    style_tang_dynasty: {
      cover:
        "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=900&q=80",
      verticalName: "盛唐气象",
    },
    style_han_dynasty: {
      cover:
        "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=900&q=80",
      verticalName: "汉代风骨",
    },
    style_xianxia: {
      cover:
        "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=900&q=80",
      verticalName: "仙侠梦幻",
    },
    style_new_chinese: {
      cover:
        "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=80",
      verticalName: "新中式感",
    },
  };

  return styles
    .filter((item) => coverMap[item.id])
    .slice(0, 4)
    .map((item) => ({
      ...item,
      cover: coverMap[item.id].cover,
      verticalName: coverMap[item.id].verticalName,
    }));
});

const galleryItems = [
  {
    title: "云裳神女",
    image:
      "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?auto=format&fit=crop&w=720&q=80",
  },
  {
    title: "墨客寻梅",
    image:
      "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=720&q=80",
  },
  {
    title: "花钿弄影",
    image:
      "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=720&q=80",
  },
  {
    title: "平湖秋月",
    image:
      "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=720&q=80",
  },
];

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
  min-height: 820px;
  max-width: 1280px;
  margin: 0 auto;
  padding: 88px 40px 56px;
}

.hero-copy {
  max-width: 560px;
}

.hero-kicker {
  margin: 0 0 18px;
  color: rgba(120, 44, 29, 0.78);
  font-size: 14px;
  letter-spacing: 0.16em;
}

.hero-copy h1 {
  margin: 0;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 60px;
  line-height: 1.12;
  font-weight: 700;
}

.hero-copy h1 span {
  color: #c53f25;
}

.hero-description {
  max-width: 470px;
  margin: 22px 0 0;
  color: rgba(34, 34, 34, 0.72);
  font-size: 16px;
  line-height: 1.85;
}

.hero-actions {
  display: flex;
  gap: 16px;
  margin-top: 34px;
}

.primary-button,
.secondary-button,
.cta-button,
.gallery-link {
  text-decoration: none;
}

.primary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 138px;
  height: 52px;
  padding: 0 24px;
  border-radius: 10px;
  background: linear-gradient(135deg, #d94b2b, #b62b11);
  box-shadow: 0 10px 24px rgba(183, 45, 20, 0.22);
  color: #fff;
  font-weight: 600;
}

.secondary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 138px;
  height: 52px;
  padding: 0 24px;
  border: 1px solid rgba(23, 23, 23, 0.08);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.82);
  color: #171717;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.content-section,
.cta-section,
.home-footer {
  width: min(1280px, calc(100vw - 48px));
  margin: 0 auto;
}

.section-title,
.section-heading {
  margin-bottom: 28px;
}

.section-title.with-line {
  display: flex;
  align-items: center;
  gap: 16px;
}

.section-title.with-line span {
  width: 52px;
  height: 1px;
  background: #d8af56;
}

.section-title h2,
.section-heading h2,
.cta-section h2 {
  margin: 0;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 36px;
  line-height: 1.2;
  font-weight: 600;
}

.section-heading p,
.cta-section p,
.home-footer p {
  margin: 10px 0 0;
  color: rgba(34, 34, 34, 0.6);
  line-height: 1.8;
}

.section-heading.center {
  text-align: center;
}

.section-heading.between {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
}

.style-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.style-card {
  position: relative;
  aspect-ratio: 0.72;
  overflow: hidden;
  padding: 0;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 14px;
  background: #111;
  cursor: pointer;
  transition:
    transform 0.28s ease,
    box-shadow 0.28s ease;
  box-shadow: 0 14px 34px rgba(17, 17, 17, 0.12);
}

.style-card:hover,
.inspiration-large:hover,
.inspiration-small:hover,
.gallery-card:hover {
  transform: translateY(-6px);
}

.style-card img,
.inspiration-large img,
.inspiration-small img,
.gallery-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.style-card-overlay,
.inspiration-overlay,
.gallery-hover {
  position: absolute;
  inset: 0;
}

.style-card-overlay {
  background: linear-gradient(180deg, rgba(17, 17, 17, 0.12), rgba(17, 17, 17, 0.8));
}

.style-card-label {
  position: absolute;
  top: 18px;
  right: 18px;
  z-index: 1;
}

.style-card-label span {
  display: inline-block;
  padding: 8px 6px;
  background: rgba(17, 17, 17, 0.2);
  color: #fff;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 22px;
  line-height: 1.2;
  letter-spacing: 0.08em;
  writing-mode: vertical-rl;
  text-orientation: mixed;
}

.inspiration-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(340px, 1fr);
  gap: 24px;
  min-height: 620px;
}

.inspiration-large,
.inspiration-small {
  position: relative;
  overflow: hidden;
  padding: 0;
  border: 1px solid rgba(255, 255, 255, 0.32);
  border-radius: 18px;
  background: #111;
  cursor: pointer;
  box-shadow: 0 18px 46px rgba(17, 17, 17, 0.12);
  transition: transform 0.28s ease;
}

.inspiration-side {
  display: grid;
  grid-template-rows: 1fr 1fr;
  gap: 24px;
}

.inspiration-overlay {
  background: linear-gradient(180deg, rgba(17, 17, 17, 0.08), rgba(17, 17, 17, 0.82));
}

.inspiration-copy {
  position: absolute;
  inset-inline: 0;
  bottom: 0;
  z-index: 1;
  padding: 28px;
  text-align: left;
  color: #fff;
}

.inspiration-copy h3 {
  margin: 0 0 10px;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 30px;
  font-weight: 600;
}

.inspiration-copy p {
  margin: 0;
  color: rgba(255, 255, 255, 0.72);
  line-height: 1.75;
}

.inspiration-copy.compact h3 {
  font-size: 24px;
  margin-bottom: 6px;
}

.inspiration-tag {
  display: inline-flex;
  align-items: center;
  height: 30px;
  padding: 0 14px;
  margin-bottom: 14px;
  border-radius: 999px;
  background: rgba(79, 121, 106, 0.88);
  font-size: 12px;
  letter-spacing: 0.1em;
}

.gallery-link {
  color: #bf3d21;
  font-weight: 600;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.gallery-card {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 12px;
  box-shadow: 0 10px 28px rgba(17, 17, 17, 0.1);
  transition: transform 0.28s ease;
}

.gallery-hover {
  display: flex;
  align-items: flex-end;
  padding: 14px;
  background: linear-gradient(180deg, rgba(17, 17, 17, 0), rgba(17, 17, 17, 0.64));
  color: #fff;
}

.cta-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 88px 24px 64px;
  text-align: center;
  border-top: 1px solid rgba(17, 17, 17, 0.06);
  border-bottom: 1px solid rgba(17, 17, 17, 0.06);
}

.cta-mark {
  position: relative;
  width: 54px;
  height: 54px;
  margin: 0 auto 30px;
  border: 1.5px solid #c33f23;
  transform: rotate(45deg);
}

.cta-mark::after {
  content: "梦";
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: #c33f23;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 18px;
  font-weight: 600;
  transform: rotate(-45deg);
}

.cta-section h2 {
  font-size: 42px;
}

.cta-section p {
  max-width: 760px;
  margin-top: 18px;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 220px;
  height: 52px;
  margin-top: 34px;
  padding: 0 28px;
  background: #c63e23;
  color: #fff;
  font-weight: 600;
}

.home-footer {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  padding-top: 12px;
}

.footer-brand strong {
  display: block;
  margin-bottom: 10px;
  color: rgba(23, 23, 23, 0.42);
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 30px;
}

.footer-brand p {
  max-width: 360px;
  margin: 0;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  gap: 26px;
  padding-top: 18px;
}

.footer-links a {
  color: rgba(34, 34, 34, 0.62);
  text-decoration: none;
}

@media (max-width: 1100px) {
  .hero-section,
  .hero-content {
    min-height: 720px;
  }

  .hero-copy h1 {
    font-size: 48px;
  }

  .style-grid,
  .gallery-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .inspiration-layout {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .inspiration-large {
    min-height: 520px;
  }
}

@media (max-width: 720px) {
  .home-page {
    gap: 56px;
  }

  .content-section,
  .cta-section,
  .home-footer {
    width: min(100vw - 32px, 1280px);
  }

  .hero-content {
    padding: 92px 20px 42px;
    align-items: flex-start;
  }

  .hero-copy h1 {
    font-size: 38px;
  }

  .hero-description {
    font-size: 15px;
  }

  .hero-actions,
  .section-heading.between,
  .home-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .style-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .gallery-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .section-title h2,
  .section-heading h2,
  .cta-section h2 {
    font-size: 28px;
  }

  .inspiration-large,
  .inspiration-small {
    min-height: 360px;
  }

  .inspiration-copy h3 {
    font-size: 24px;
  }
}
</style>
