<template>
  <div class="workspace-page">
    <div class="workspace-grid">
      <div class="left-column">
        <section class="panel prompt-panel">
          <div class="section-head">
            <h2>灵感描绘</h2>
            <span class="counter">{{ prompt.length }} / 500</span>
          </div>
          <textarea
            v-model="prompt"
            class="prompt-input"
            placeholder="描述你想生成的国风角色，例如：盛唐时期丰腴贵族女子，金色步摇，红色齐胸襦裙，端庄华贵"
          />
          <div class="prompt-actions">
            <button
              v-for="item in recommendedPrompts"
              :key="item"
              type="button"
              class="pill-button"
              @click="prompt = item"
            >
              {{ item }}
            </button>
          </div>
        </section>

        <section class="panel">
          <div class="section-head">
            <h2>风格选择</h2>
          </div>
          <div class="style-grid">
            <button
              v-for="style in styleCards"
              :key="style.id"
              type="button"
              class="style-card"
              :class="{ active: selectedStyleId === style.id }"
              @click="selectedStyleId = style.id"
            >
              <img :src="style.image" :alt="style.name" />
              <div class="style-overlay"></div>
              <div class="style-copy">
                <strong>{{ style.name }}</strong>
                <span>{{ style.description }}</span>
              </div>
            </button>
          </div>
        </section>

        <section class="panel">
          <div class="section-head">
            <h2>模板选择</h2>
          </div>
          <div class="template-grid">
            <button
              v-for="template in templateCards"
              :key="template.id"
              type="button"
              class="template-card"
              :class="{ active: selectedTemplateId === template.id }"
              @click="selectedTemplateId = template.id"
            >
              <strong>{{ template.name }}</strong>
              <p>{{ template.scene }}</p>
              <div class="template-meta">
                <span>+{{ template.extraPoints }} 积分</span>
              </div>
            </button>
          </div>
        </section>

        <div class="bottom-grid">
          <section class="panel">
            <div class="section-head compact">
              <h2>比例枚举</h2>
            </div>
            <div class="ratio-list">
              <button
                v-for="ratio in ratioCards"
                :key="ratio.id"
                type="button"
                class="ratio-card"
                :class="{ active: selectedRatioId === ratio.id }"
                @click="selectedRatioId = ratio.id"
              >
                <div>
                  <strong>{{ ratio.label }} {{ ratio.title }}</strong>
                  <p>{{ ratio.scene }}</p>
                  <small>{{ ratio.resolution }}</small>
                </div>
              </button>
            </div>
          </section>

          <section class="panel">
            <div class="section-head compact">
              <h2>参考图</h2>
              <span class="muted">最多 3 张</span>
            </div>
            <div class="reference-grid">
              <button type="button" class="upload-box" @click="increaseReference">上传</button>
              <div
                v-for="item in referenceSlots"
                :key="item"
                class="reference-thumb"
                :class="{ filled: item <= referenceImageCount }"
              ></div>
            </div>
            <div class="reference-mode-row">
              <strong>参考模式</strong>
              <select v-model="selectedReferenceMode" class="reference-select">
                <option v-for="mode in referenceModesDisplay" :key="mode.id" :value="mode.id">
                  {{ mode.name }}
                </option>
              </select>
            </div>
          </section>
        </div>
      </div>

      <div class="right-column">
        <section class="preview-card">
          <img :src="currentPreviewImage" :alt="currentStyleLabel" />
          <div class="preview-caption">当前预览：{{ currentStyleLabel }}</div>
        </section>

        <section class="side-panel quality-panel">
          <div class="section-head compact">
            <h2>生成质量</h2>
          </div>
          <div class="quality-row">
            <button
              v-for="quality in qualityDisplay"
              :key="quality.id"
              type="button"
              class="quality-chip"
              :class="{ active: selectedQualityLevel === quality.id }"
              @click="selectedQualityLevel = quality.id"
            >
              {{ quality.name }}
            </button>
          </div>

          <div class="cost-box">
            <div class="cost-head">
              <span>消耗估算</span>
              <strong>{{ quote.finalPoints }} 积分</strong>
            </div>
            <p>
              基础 {{ quote.basePoints }} + 风格 {{ quote.styleExtraPoints }} + 模板 {{ quote.templateExtraPoints }} +
              参考图 {{ quote.referenceImageExtraPoints }}
            </p>
          </div>

          <button class="start-button" type="button" :disabled="submitting" @click="submitTask">
            立即生成
          </button>
          <p class="queue-tip">AI 正在绘制中预计 10~30 秒，提交后将进入绘制页。</p>
          <p v-if="submitMessage" class="submit-message">{{ submitMessage }}</p>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ApiClient } from "@/api/client";
import { DreamDrawApi } from "@/api/dream-draw";
import { qualityLevels, ratios, referenceImageModes, styles, templates } from "@/shared/catalog";
import { useSessionStore } from "@/stores/session";
import { buildQuotePreview, getPromptLengthState } from "@/utils/pricing";

const route = useRoute();
const router = useRouter();
const session = useSessionStore();
const api = new DreamDrawApi(
  new ApiClient({
    getToken: () => session.userToken,
  }),
);

const prompt = ref((route.query.prompt as string) || "盛唐时期丰腴贵族女子，金色步摇，红色齐胸襦裙，端庄华贵");
const selectedStyleId = ref((route.query.style as string) || styles[0].id);
const selectedTemplateId = ref((route.query.template as string) || templates[0].id);
const selectedRatioId = ref(ratios[0].id);
const selectedQualityLevel = ref(qualityLevels[0].id);
const selectedReferenceMode = ref(referenceImageModes[0].id);
const referenceImageCount = ref(0);
const submitting = ref(false);
const submitMessage = ref("");

const recommendedPrompts = ["盛唐贵族女子", "仙侠白衣少女", "新中式冷艳女性"];
const styleCards = styles.map((item) => ({
  ...item,
  image:
    {
      style_tang_dynasty:
        "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80",
      style_han_dynasty:
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
      style_xianxia:
        "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=800&q=80",
      style_new_chinese:
        "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=800&q=80",
      style_gufeng_portrait:
        "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=800&q=80",
      style_cinematic:
        "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=800&q=80",
    }[item.id] ?? "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80",
}));
const templateCards = templates;
const ratioCards = ratios;
const qualityDisplay = qualityLevels;
const referenceModesDisplay = referenceImageModes;
const referenceSlots = [1, 2, 3];

const quote = computed(() =>
  buildQuotePreview({
    styleId: selectedStyleId.value,
    templateId: selectedTemplateId.value,
    ratioId: selectedRatioId.value,
    qualityLevel: selectedQualityLevel.value,
    referenceImageCount: referenceImageCount.value,
  }),
);

const currentStyleLabel = computed(() => {
  return styles.find((item) => item.id === selectedStyleId.value)?.name ?? "";
});

const currentPreviewImage = computed(() => {
  const map: Record<string, string> = {
    style_tang_dynasty:
      "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80",
    style_han_dynasty:
      "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
    style_xianxia:
      "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=800&q=80",
    style_new_chinese:
      "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=800&q=80",
    style_gufeng_portrait:
      "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=800&q=80",
    style_cinematic:
      "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=800&q=80",
  };
  return map[selectedStyleId.value] || map.style_tang_dynasty;
});

function increaseReference() {
  referenceImageCount.value = Math.min(3, referenceImageCount.value + 1);
}

async function submitTask() {
  if (getPromptLengthState(prompt.value) === "prompt_over_limit" || !prompt.value.trim()) {
    submitMessage.value = "请把 Prompt 控制在 1 到 300 字内。";
    return;
  }
  if (!session.isAuthenticated) {
    await router.push({
      name: "login",
      query: { redirect: "/workspace" },
    });
    return;
  }

  submitting.value = true;
  submitMessage.value = "";
  try {
    const result = await api.createTask({
      prompt: prompt.value,
      ratio_id: selectedRatioId.value,
      style_id: selectedStyleId.value,
      template_id: selectedTemplateId.value,
      quality_level: selectedQualityLevel.value,
      reference_mode: selectedReferenceMode.value,
      reference_image_urls: Array.from({ length: referenceImageCount.value }, (_, index) => {
        return `https://example.com/reference-${index + 1}.png`;
      }),
    });
    session.setPointsBalance((session.pointsBalance ?? 0) - result.final_points);
    await router.push({
      name: "generating",
      query: { taskId: String(result.task_id) },
    });
  } catch (error) {
    submitMessage.value = error instanceof Error ? error.message : "生成失败，请稍后再试";
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.workspace-page {
  padding-bottom: 28px;
}

.workspace-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) 380px;
  gap: 22px;
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.panel,
.side-panel,
.preview-card {
  border-radius: 26px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 18px 42px rgba(31, 26, 22, 0.06);
}

.panel {
  padding: 26px 28px;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.section-head h2 {
  margin: 0;
  color: #171717;
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 22px;
}

.counter,
.muted {
  color: rgba(79, 67, 59, 0.56);
  font-size: 14px;
}

.prompt-input {
  width: 100%;
  min-height: 250px;
  border: 0;
  border-radius: 22px;
  padding: 26px 24px;
  background: #fff;
  color: #201a18;
  font-size: 18px;
  line-height: 1.7;
  resize: vertical;
  box-shadow: inset 0 0 0 1px rgba(230, 223, 216, 0.88);
}

.prompt-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 18px;
}

.pill-button {
  min-width: 94px;
  height: 42px;
  border: 1px solid rgba(219, 211, 203, 0.92);
  border-radius: 999px;
  background: #faf7f4;
  color: #5c4840;
  cursor: pointer;
}

.style-grid,
.template-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.style-card,
.template-card,
.ratio-card {
  border-radius: 18px;
  cursor: pointer;
}

.style-card {
  position: relative;
  overflow: hidden;
  aspect-ratio: 0.72;
  padding: 0;
  border: 2px solid transparent;
  background: #111;
}

.style-card.active,
.template-card.active,
.ratio-card.active {
  border-color: #d9b332;
}

.style-card img,
.preview-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.style-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.72));
}

.style-copy {
  position: absolute;
  left: 16px;
  right: 16px;
  bottom: 16px;
  color: #fff;
  text-align: left;
}

.style-copy strong {
  display: block;
  font-size: 18px;
}

.template-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 140px;
  padding: 18px;
  border: 1px solid rgba(233, 225, 216, 0.94);
  background: #fff;
  color: #2b211e;
  text-align: left;
}

.template-card p,
.ratio-card p {
  margin: 0;
  color: #6c564c;
  line-height: 1.6;
}

.template-meta {
  margin-top: auto;
  color: #cc5b3c;
}

.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.ratio-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.ratio-card {
  display: flex;
  align-items: center;
  gap: 16px;
  min-height: 84px;
  padding: 16px 18px;
  border: 2px solid rgba(227, 222, 214, 0.92);
  background: #fff;
  color: #302522;
  text-align: left;
}

.ratio-card small {
  color: rgba(88, 72, 63, 0.7);
}

.reference-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}

.upload-box,
.reference-thumb {
  height: 88px;
  border-radius: 18px;
}

.upload-box {
  border: 1px dashed rgba(214, 154, 116, 0.72);
  background: rgba(252, 246, 239, 0.9);
  color: #a46a42;
  cursor: pointer;
}

.reference-thumb {
  background: linear-gradient(180deg, rgba(249, 245, 240, 0.92), rgba(241, 234, 227, 0.9));
  border: 1px solid rgba(230, 220, 211, 0.9);
}

.reference-thumb.filled {
  background: linear-gradient(160deg, #dcb07b, #9b6758);
}

.reference-mode-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.reference-select {
  flex: 1;
  height: 42px;
  border-radius: 14px;
  border: 1px solid rgba(227, 218, 208, 0.96);
  padding: 0 16px;
  background: #fff;
}

.preview-card {
  position: relative;
  overflow: hidden;
  min-height: 480px;
}

.preview-caption {
  position: absolute;
  left: 22px;
  right: 22px;
  bottom: 22px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(20, 20, 20, 0.38);
  color: #fff;
  backdrop-filter: blur(10px);
}

.quality-panel {
  padding: 24px;
}

.quality-row {
  display: flex;
  gap: 12px;
}

.quality-chip {
  flex: 1;
  height: 42px;
  border-radius: 999px;
  border: 1px solid rgba(225, 217, 209, 0.92);
  background: #fff;
  color: #4b3e38;
  cursor: pointer;
}

.quality-chip.active {
  border-color: transparent;
  background: linear-gradient(135deg, #d9b131, #e7c75a);
  color: #fff;
}

.cost-box {
  margin-top: 22px;
  padding: 18px 20px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(255, 247, 232, 0.94), rgba(255, 244, 244, 0.94));
  color: #5d4036;
}

.cost-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 10px;
}

.cost-head strong {
  font-size: 24px;
  color: #d5482d;
}

.start-button {
  width: 100%;
  height: 54px;
  margin-top: 24px;
  border: 0;
  border-radius: 999px;
  background: linear-gradient(135deg, #d53a25, #f05a2b);
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  box-shadow: 0 18px 30px rgba(224, 74, 39, 0.22);
}

.start-button:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.queue-tip,
.submit-message {
  margin: 14px 2px 0;
  color: rgba(95, 77, 69, 0.78);
  line-height: 1.7;
}

.submit-message {
  color: #b74a2a;
}

@media (max-width: 1220px) {
  .workspace-grid {
    grid-template-columns: 1fr;
  }

  .right-column {
    order: -1;
  }

  .preview-card {
    min-height: 420px;
  }
}

@media (max-width: 860px) {
  .panel,
  .quality-panel {
    padding: 22px;
  }

  .style-grid,
  .template-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 620px) {
  .workspace-page {
    padding-bottom: 24px;
  }

  .style-grid,
  .template-grid {
    grid-template-columns: 1fr;
  }

  .reference-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
