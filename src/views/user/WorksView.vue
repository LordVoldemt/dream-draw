<template>
  <div class="works-page">
    <div class="page-background"></div>

    <section class="archive-hero">
      <div class="hero-left">
        <div class="hero-title">
          <h1>作品库</h1>
          <span>My Creative Archive</span>
        </div>

        <div class="tab-row">
          <button
            v-for="tab in tabs"
            :key="tab"
            type="button"
            class="tab"
            :class="{ active: tab === activeTab }"
            @click="activeTab = tab"
          >
            {{ tab }}
          </button>
        </div>
      </div>

      <div class="hero-right">
        <RouterLink class="create-button" to="/workspace">立即生成</RouterLink>
        <div class="count-row">
          <span>共 {{ filteredWorks.length }} 件作品</span>
        </div>
      </div>
    </section>

    <div v-if="loading" class="state-card">正在加载你的作品...</div>
    <div v-else-if="filteredWorks.length === 0" class="state-card empty-state">
      <p>{{ emptyText }}</p>
      <RouterLink to="/workspace">去生成工作台</RouterLink>
    </div>
    <section v-else class="works-grid">
      <article v-for="work in filteredWorks" :key="work.id" class="work-card">
        <div class="work-visual">
          <img :src="String(work.image_url || fallbackImage(work.style_id))" :alt="resolveTemplateLabel(work.template_id)" />
          <div class="work-tags">
            <span>{{ resolveStyleLabel(work.style_id) }}</span>
            <span>{{ resolveTemplateLabel(work.template_id) }}</span>
          </div>
        </div>
        <div class="work-content">
          <strong>{{ resolveTemplateLabel(work.template_id) }}</strong>
          <p>{{ formatDate(String(work.created_at)) }} 生成</p>
          <div class="actions">
            <RouterLink :to="`/result/${work.id}`">查看</RouterLink>
            <button type="button" @click="share(Number(work.id))">分享</button>
            <button type="button" @click="toggleFavorite(work)">
              {{ work.is_favorite ? "取消收藏" : "收藏" }}
            </button>
          </div>
        </div>
      </article>
    </section>

    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { ApiClient } from "@/api/client";
import { DreamDrawApi } from "@/api/dream-draw";
import { styles, templates } from "@/shared/catalog";
import { useSessionStore } from "@/stores/session";

type WorkRecord = {
  id: number;
  style_id: string;
  template_id: string;
  created_at: string;
  image_url?: string | null;
  is_favorite?: boolean;
};

const session = useSessionStore();
const api = new DreamDrawApi(
  new ApiClient({
    getToken: () => session.userToken,
  }),
);

const tabs = ["我的作品", "收藏作品", "最近生成"];
const activeTab = ref("我的作品");
const loading = ref(true);
const works = ref<WorkRecord[]>([]);
const message = ref("");

const filteredWorks = computed(() => {
  const items = [...works.value];
  if (activeTab.value === "收藏作品") {
    return items.filter((item) => item.is_favorite);
  }
  if (activeTab.value === "最近生成") {
    return items.sort((a, b) => String(b.created_at).localeCompare(String(a.created_at))).slice(0, 8);
  }
  return items;
});

const emptyText = computed(() => {
  if (activeTab.value === "收藏作品") return "你还没有收藏作品，先去结果页收藏喜欢的角色。";
  if (activeTab.value === "最近生成") return "最近还没有生成记录，先去试试第一张国风角色。";
  return "你还没有作品，先去生成第一张国风角色吧。";
});

function fallbackImage(styleId: string) {
  const imageMap: Record<string, string> = {
    style_tang_dynasty:
      "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=900&q=80",
    style_han_dynasty:
      "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=900&q=80",
    style_xianxia:
      "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=80",
    style_new_chinese:
      "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=900&q=80",
  };
  return imageMap[styleId] || imageMap.style_tang_dynasty;
}

function resolveStyleLabel(styleId: string) {
  return styles.find((item) => item.id === styleId)?.name ?? styleId;
}

function resolveTemplateLabel(templateId: string) {
  return templates.find((item) => item.id === templateId)?.name ?? templateId;
}

function formatDate(value: string) {
  return value ? value.slice(0, 10).replace(/-/g, ".") : "";
}

async function loadWorks() {
  loading.value = true;
  try {
    const response = await api.getWorks();
    works.value = response.works as WorkRecord[];
  } catch (error) {
    message.value = error instanceof Error ? error.message : "作品加载失败";
  } finally {
    loading.value = false;
  }
}

async function share(workId: number) {
  try {
    const response = await api.shareWork(workId, "wechat");
    message.value = `分享链接已生成：${response.share_payload.share_link}`;
  } catch (error) {
    message.value = error instanceof Error ? error.message : "分享失败";
  }
}

async function toggleFavorite(work: WorkRecord) {
  if (work.is_favorite) {
    await api.unfavoriteWork(work.id);
    work.is_favorite = false;
    return;
  }
  await api.favoriteWork(work.id);
  work.is_favorite = true;
}

onMounted(() => {
  void loadWorks();
});
</script>

<style scoped>
.works-page {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 36px;
  padding-bottom: 28px;
  overflow: hidden;
}

.page-background {
  position: absolute;
  inset: 0;
  z-index: 0;
  background:
    radial-gradient(circle at 20% 20%, rgba(255, 177, 97, 0.55), transparent 28%),
    radial-gradient(circle at 78% 30%, rgba(86, 197, 227, 0.58), transparent 34%),
    radial-gradient(circle at 62% 82%, rgba(255, 170, 80, 0.56), transparent 25%),
    linear-gradient(90deg, rgba(71, 191, 226, 0.88) 0%, rgba(246, 198, 135, 0.86) 50%, rgba(69, 188, 226, 0.86) 100%);
  opacity: 0.88;
  pointer-events: none;
}

.archive-hero,
.works-grid,
.message,
.state-card {
  position: relative;
  z-index: 1;
}

.archive-hero {
  display: flex;
  justify-content: space-between;
  gap: 32px;
  padding: 54px 16px 18px;
}

.hero-title {
  display: flex;
  align-items: baseline;
  gap: 18px;
}

.hero-title h1 {
  margin: 0;
  color: #161616;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 56px;
  line-height: 1.1;
}

.hero-title span {
  color: #5f4d46;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 24px;
}

.tab-row {
  display: flex;
  gap: 28px;
  margin-top: 34px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.55);
}

.tab {
  border: 0;
  padding: 0;
  background: transparent;
  color: #573f38;
  font-size: 20px;
  font-weight: 600;
  cursor: pointer;
}

.tab.active {
  color: #d64527;
}

.hero-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: flex-end;
  gap: 24px;
  min-width: 240px;
}

.create-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 186px;
  height: 58px;
  border-radius: 12px;
  background: linear-gradient(135deg, #d3472a, #c94122);
  color: #fff;
  font-size: 22px;
  text-decoration: none;
}

.count-row {
  color: #4c433f;
  font-size: 18px;
}

.state-card {
  padding: 32px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.8);
  color: #574740;
}

.empty-state a {
  color: #d64527;
}

.works-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 28px;
}

.work-card {
  overflow: hidden;
  border-radius: 24px;
  background: rgba(237, 252, 253, 0.82);
  box-shadow: 0 18px 36px rgba(36, 31, 28, 0.08);
}

.work-visual {
  position: relative;
  aspect-ratio: 0.82;
}

.work-visual img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.work-tags {
  position: absolute;
  top: 18px;
  left: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.work-tags span {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  min-height: 34px;
  padding: 0 16px;
  border-radius: 999px;
  background: rgba(89, 132, 116, 0.92);
  color: #fff;
  font-size: 15px;
}

.work-tags span:last-child {
  background: rgba(255, 255, 255, 0.92);
  color: #2d2522;
}

.work-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 18px 20px 20px;
}

.work-content strong {
  color: #1c1715;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 28px;
  line-height: 1.2;
}

.work-content p {
  margin: 0;
  color: #5f4b43;
  font-size: 16px;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.actions a,
.actions button {
  border: 0;
  background: transparent;
  color: #4b3632;
  font-size: 16px;
  text-decoration: none;
  cursor: pointer;
}

.message {
  margin: 0;
  color: #583f37;
  text-align: center;
}

@media (max-width: 1200px) {
  .works-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .archive-hero {
    flex-direction: column;
  }

  .hero-right {
    align-items: flex-start;
  }

  .works-grid {
    grid-template-columns: 1fr;
  }

  .hero-title {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
