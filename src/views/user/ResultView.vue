<template>
  <div class="result-page">
    <div v-if="loading" class="state-card">正在加载生成结果...</div>
    <div v-else-if="!work" class="state-card">未找到对应作品，请返回作品页重试。</div>
    <template v-else>
      <section class="hero-grid">
        <div class="image-panel">
          <img :src="heroImage" alt="生成结果" />
          <div class="vertical-label">{{ currentStyleLabel }}</div>
        </div>

        <div class="side-column">
          <article class="info-card">
            <h2>生成参数</h2>
            <div class="prompt-box">“{{ String(work.prompt_snapshot || "") }}”</div>
            <div class="tag-row">
              <span v-for="tag in resultTags" :key="tag">{{ tag }}</span>
            </div>
            <div class="action-grid">
              <button class="primary-action" type="button" @click="downloadImage">下载原图</button>
              <button class="secondary-action" type="button" @click="goRecreate">再次生成</button>
            </div>
            <button class="favorite-button" type="button" @click="toggleFavorite">
              {{ isFavorite ? "取消收藏" : "收藏此作" }}
            </button>
          </article>

          <article class="share-card">
            <h2>分享灵感</h2>
            <div class="share-layout">
              <div class="poster-preview">分享海报</div>
              <div class="share-copy">
                <p>生成分享海报，展示你的国风美学角色，带动分享回流再生成。</p>
                <div class="share-buttons">
                  <button v-for="channel in shareChannels" :key="channel.id" type="button" @click="share(channel.id)">
                    {{ channel.label }}
                  </button>
                </div>
              </div>
            </div>
            <p v-if="shareMessage" class="share-message">{{ shareMessage }}</p>
          </article>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ApiClient } from "@/api/client";
import { DreamDrawApi } from "@/api/dream-draw";
import { referenceImageModes, styles, templates } from "@/shared/catalog";
import { useSessionStore } from "@/stores/session";

type WorkRecord = Record<string, unknown>;

const route = useRoute();
const router = useRouter();
const session = useSessionStore();
const api = new DreamDrawApi(
  new ApiClient({
    getToken: () => session.userToken,
  }),
);

const loading = ref(true);
const work = ref<WorkRecord | null>(null);
const shareMessage = ref("");
const shareChannels = [
  { id: "xiaohongshu", label: "小红书" },
  { id: "wechat", label: "微信" },
  { id: "qq", label: "QQ" },
  { id: "weibo", label: "微博" },
];

const heroImage = computed(() => {
  return String(work.value?.image_url ?? "");
});

const isFavorite = computed(() => Boolean(work.value?.is_favorite));

const currentStyleLabel = computed(() => {
  const styleId = String(work.value?.style_id ?? "");
  return styles.find((item) => item.id === styleId)?.name ?? styleId;
});

const resultTags = computed(() => {
  const templateLabel =
    templates.find((item) => item.id === String(work.value?.template_id ?? ""))?.name ?? "模板";
  const ratioLabel = String(work.value?.ratio_id ?? "");
  const qualityLabel = String(work.value?.quality_level ?? "");
  const referenceMode =
    referenceImageModes.find((item) => item.id === String(work.value?.reference_mode ?? ""))?.name ?? "无参考模式";
  return [
    currentStyleLabel.value,
    templateLabel,
    ratioLabel,
    qualityLabel,
    `${referenceMode} / ${String(work.value?.reference_image_count ?? 0)} 张`,
    `${String(work.value?.final_points ?? 0)} 积分`,
  ];
});

async function loadWork() {
  loading.value = true;
  try {
    const response = await api.getWorkDetail(Number(route.params.id));
    work.value = response.work;
  } finally {
    loading.value = false;
  }
}

function downloadImage() {
  shareMessage.value = `下载地址：${String(work.value?.image_url ?? "")}`;
}

function goRecreate() {
  void router.push({
    name: "workspace",
    query: {
      style: String(work.value?.style_id ?? ""),
      template: String(work.value?.template_id ?? ""),
      prompt: String(work.value?.prompt_snapshot ?? ""),
    },
  });
}

async function toggleFavorite() {
  if (!work.value) return;
  if (isFavorite.value) {
    await api.unfavoriteWork(Number(work.value.id));
    work.value = { ...work.value, is_favorite: false };
    return;
  }
  await api.favoriteWork(Number(work.value.id));
  work.value = { ...work.value, is_favorite: true };
}

async function share(channel: string) {
  if (!work.value) return;
  const response = await api.shareWork(Number(work.value.id), channel);
  shareMessage.value = `${channel} 分享链接：${response.share_payload.share_link}`;
}

onMounted(() => {
  void loadWork();
});
</script>

<style scoped>
.result-page {
  display: flex;
  flex-direction: column;
  gap: 48px;
  padding-bottom: 28px;
}

.state-card {
  padding: 40px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  color: #6d5950;
}

.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) 404px;
  gap: 24px;
}

.image-panel,
.info-card,
.share-card {
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 42px rgba(36, 31, 28, 0.06);
}

.image-panel {
  position: relative;
  padding: 14px;
}

.image-panel img {
  width: 100%;
  height: 100%;
  min-height: 760px;
  object-fit: cover;
  border-radius: 18px;
}

.vertical-label {
  position: absolute;
  top: 32px;
  left: 32px;
  padding: 12px 10px;
  background: #d44427;
  color: #fff;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 22px;
  line-height: 1.15;
  writing-mode: vertical-rl;
  text-orientation: mixed;
}

.side-column {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.info-card,
.share-card {
  padding: 28px;
}

.info-card h2,
.share-card h2 {
  margin: 0 0 18px;
  color: #171717;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 30px;
}

.prompt-box {
  padding: 18px;
  border: 1px solid rgba(232, 220, 212, 0.95);
  border-radius: 14px;
  color: #54453f;
  line-height: 1.9;
  background: #fffdfa;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.tag-row span {
  padding: 8px 14px;
  border-radius: 999px;
  background: #edf7f1;
  color: #58806f;
  font-size: 14px;
}

.action-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-top: 28px;
}

.primary-action,
.secondary-action,
.favorite-button,
.share-buttons button {
  height: 56px;
  border-radius: 12px;
  font-size: 18px;
  cursor: pointer;
}

.primary-action {
  border: 0;
  background: linear-gradient(135deg, #d3482a, #c93f22);
  color: #fff;
}

.secondary-action,
.favorite-button {
  border: 1px solid rgba(233, 224, 217, 0.94);
  background: #fff;
  color: #2e2522;
}

.favorite-button {
  width: 100%;
  margin-top: 14px;
}

.share-layout {
  display: grid;
  grid-template-columns: 92px 1fr;
  gap: 18px;
  align-items: center;
}

.poster-preview {
  display: grid;
  place-items: center;
  width: 82px;
  height: 120px;
  border-radius: 12px;
  background: linear-gradient(180deg, #f6f6f6, #ebebeb);
  color: #9d948f;
  font-size: 14px;
}

.share-copy p {
  margin: 0 0 14px;
  color: #5e4d45;
  line-height: 1.7;
}

.share-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.share-buttons button {
  min-width: 96px;
  border: 1px solid rgba(222, 230, 224, 0.94);
  background: #f8fbf8;
  color: #446f60;
}

.share-message {
  margin: 14px 0 0;
  color: #6a574d;
  font-size: 14px;
}

@media (max-width: 1200px) {
  .hero-grid {
    grid-template-columns: 1fr;
  }

  .image-panel img {
    min-height: 520px;
  }
}

@media (max-width: 900px) {
  .action-grid,
  .share-layout {
    grid-template-columns: 1fr;
  }
}
</style>
