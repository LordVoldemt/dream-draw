# Round Closeout: 垂直型 AI 国风角色生成平台

**日期**: 2026-05-19  
**状态**: 待确认

## 1. 本轮范围

- 完成 `T001-T046` 全部实现与验证
- 交付用户端页面、管理端页面、后端 API、数据库 schema、模型配置与监控能力
- 补齐集成测试、风控测试、README 与 ADPP 任务状态

## 2. 改动面扫描

### Closeout 策略摘要

- 当前变更：`.adpp/changes/2026-05-18-guofeng-character-platform`
- source_of_truth_docs：4 个
- derived_docs：1 个
- verification_layers：2 层（base + trigger-specific）
- evidence_dirs：3 个（`coverage/`、`test-results/`、`output/`）

### 改动面

- 代码路径：
  - `backend/**`
  - `src/**`
  - `shared/**`
  - `tests/**`
- 文档路径：
  - `.adpp/changes/2026-05-18-guofeng-character-platform/tasks.md`
  - `README.md`
  - `.adpp/changes/2026-05-18-guofeng-character-platform/test-report.md`
  - `.adpp/changes/2026-05-18-guofeng-character-platform/closeout-note.md`
- 归类结果：
  - API / schema / contract
  - backend behavior
  - frontend behavior / UX flow
  - data / migration / script
  - docs
- 说明：
  - 当前目录不是可用 git 仓库，`git status --short` 无法执行，已按 ADPP fallback 扫描当前 feature 目录与本轮产物

## 3. 文档更新

### source_of_truth_docs

- `.adpp/changes/2026-05-18-guofeng-character-platform/tasks.md`
  - 已更新：`T001-T046` 全部标记完成
- `.adpp/changes/2026-05-18-guofeng-character-platform/prd.md`
  - 本轮未改：当前实现未改变已确认产品边界与规则
- `.adpp/changes/2026-05-18-guofeng-character-platform/design.md`
  - 本轮未改：实现遵循既有设计，没有引入超出设计的新架构方向
- `.adpp/changes/2026-05-18-guofeng-character-platform/ux-notes.md`
  - 本轮未改：页面实现已按已确认 UX 说明落地，无新增交互规则需要回写

### derived_docs

- `README.md`
  - 已更新：同步当前实现范围、本地开发方式、已验证链路和注意事项

### 新增收口文档

- `.adpp/changes/2026-05-18-guofeng-character-platform/test-report.md`
  - 已新增：记录测试命令、通过结果和风险备注
- `.adpp/changes/2026-05-18-guofeng-character-platform/closeout-note.md`
  - 已新增：记录本轮收口摘要

## 4. 验证执行

- `npm run test`
  - 结果：✅
  - 摘要：前端 11 个测试全部通过
  - 产物：无额外文件产物

- `npm run build`
  - 结果：✅
  - 摘要：前端类型检查与生产构建通过
  - 产物：`dist/`

- `pytest tests/backend -q`
  - 结果：✅
  - 摘要：后端 30 个测试全部通过
  - 产物：无额外文件产物

## 5. 证据

- `dist/`
  - 说明：前端生产构建产物目录
- `coverage/`
  - 说明：目录未生成，本轮无新增 coverage artifact
- `test-results/`
  - 说明：目录未生成，本轮无新增 test report artifact
- `output/`
  - 说明：目录未生成，本轮无新增输出 artifact
- `.adpp/changes/2026-05-18-guofeng-character-platform/test-report.md`
  - 说明：本轮验证摘要记录

## 6. 遗留风险与豁免

- 当前仓库不是可用 git 仓库，无法提供标准 git diff 级别的 closeout 审计，只能基于当前文件系统状态回收
- 前端构建存在 chunk size warning，当前不阻塞交付，但后续建议做手动拆包优化
- 当前后端仍采用 SQLite、本地默认 provider 和 mock 风格实现，生产接入时仍需替换为真实短信、支付、对象存储和模型网关
- 当前“绘制中”页面存在，但生成主链路为便于联调会直接进入最终状态，这一点已在 README 中说明

## 7. 下一步

- 执行 `$adpp-closeout` / 人工确认收口
- 如需继续推进，可进入真实基础设施接入阶段：
  - 短信服务
  - 微信/支付宝真实支付
  - MinIO 真正上传与下载
  - OpenAI-compatible 模型真实调用

## 8. 人工确认清单

▶ [人工确认] 本轮收口已完成，请确认：

- [ ] source-of-truth 文档已同步
- [ ] derived 文档已同步
- [ ] 验证已执行或已明确豁免原因
- [ ] 证据已记录
- [ ] closeout-note.md 已生成

closeout note:

- `.adpp/changes/2026-05-18-guofeng-character-platform/closeout-note.md`

---

# Round Closeout: 首页与生成页图片资产替换

**日期**: 2026-05-23 01:10:36 +08:00  
**状态**: 待确认

## 1. 本轮范围

- Scope: 替换首页与生成工作台中的远程 Unsplash 展示图片。
- 生成 13 张国风角色本地图片资产，保存到 `src/assets/home-*.jpg`。
- `HomeView.vue` 改为引用本地首页 Hero、风格卡、灵感模板与画廊图片。
- `GenerateView.vue` 改为复用本地风格图片，覆盖风格卡与右侧预览。
- 新增/补充组件测试，锁定页面展示图片不再使用远程占位链接。

## 2. 改动面扫描

- 代码路径：
  - `src/views/user/HomeView.vue`
  - `src/views/user/GenerateView.vue`
  - `src/tests/home-carousel.spec.ts`
  - `src/tests/generate-assets.spec.ts`
- 资产路径：
  - `src/assets/home-*.jpg`
- 证据路径：
  - `output/home-assets-final-contact-sheet.jpg`
- 归类结果：
  - frontend behavior / UX visual asset
  - evidence
- 说明：
  - 当前工作区存在历史未跟踪 `__pycache__/` 文件，本轮未修改也未清理。

## 3. 文档更新

### source_of_truth_docs

- `.adpp/changes/2026-05-18-guofeng-character-platform/prd.md`: 本轮未改；未改变产品边界、枚举、接口或验收标准。
- `.adpp/changes/2026-05-18-guofeng-character-platform/design.md`: 本轮未改；未改变系统架构或数据流。
- `.adpp/changes/2026-05-18-guofeng-character-platform/tasks.md`: 本轮未改；原 T023/T024/T025 已完成，本轮属于素材质量补强。
- `.adpp/changes/2026-05-18-guofeng-character-platform/ux-notes.md`: 本轮未改；未改变布局、交互流程或响应式规则，仅替换展示图片资产。

### derived_docs

- `.adpp/changes/2026-05-18-guofeng-character-platform/test-report.md`: 已更新，追加本轮测试、构建、浏览器烟测和证据路径。
- `README.md`: 本轮未改；开发方式和使用说明无变化。

## 4. 验证执行

- `npm.cmd run test -- home-carousel generate-assets`: 通过，2 个测试文件、4 个测试通过。
- `npm.cmd run test`: 通过，6 个测试文件、16 个测试通过。
- `npm.cmd run build`: 通过，`vue-tsc --noEmit && vite build` 成功；存在既有 chunk size warning。
- 浏览器烟测 `http://127.0.0.1:5174/`: 首页 13 张图片全部加载成功，断图数 0，远程展示图数 0。
- 浏览器烟测 `http://127.0.0.1:5174/workspace`: 生成工作台 7 张图片全部加载成功，断图数 0，远程展示图数 0。

## 5. 证据

- `output/home-assets-final-contact-sheet.jpg`: 本轮本地图片资产预览拼图。
- `C:\Users\jarvis\.codex\generated_images\019e5045-2c02-7f92-800e-8aef4149dc04`: 原始生成图片目录，保留未删除。

## 6. 遗留风险与豁免

- `GenerateView.vue` 中 `https://example.com/reference-*.png` 是提交生成任务时的模拟参考图请求数据，不是页面图片 `src` 展示资源，本轮不改接口行为。
- 构建报告仍提示主 chunk 超过 500 kB，属于既有打包优化问题，不阻塞本轮图片替换。

## 7. 下一步

- 由人工确认图片视觉风格是否满足最终审美偏好。
- 若后续要清理全站远程占位图片，可继续处理 `LoginView.vue`、`WorksView.vue`、`GeneratingView.vue`、`RegisterView.vue`、后台用户详情等页面。

---

# Round Closeout: 生成工作台 Prompt 润色

**日期**: 2026-05-23 01:43:00 +08:00  
**状态**: 待确认

## 1. 本轮范围

- Scope: 在生成工作台增加 Prompt 润色能力，帮助用户把短描述扩展为更完整的国风角色生成提示词。
- 新增 `POST /api/prompts/polish`，由后端读取 `model_providers` 中 `provider_id=chat` 的 OpenAI-compatible 文本模型并调用 `chat/completions`。
- 前端 `GenerateView.vue` 新增“润色”按钮、加载态、登录拦截、成功提示和失败提示，成功后替换 Prompt 输入框内容。
- 新增前后端测试覆盖润色成功、缺少 chat provider、返回格式异常、环境变量密钥引用、前端失败提示。
- 顺手修复后端回归测试的异步任务竞态、恢复重复 Prompt 防刷校验，并让真实联网图像模型测试默认跳过。

## 2. 改动面扫描

- 代码路径：
  - `backend/app/modules/generation/router.py`
  - `backend/app/services/prompt_polisher.py`
  - `backend/app/infrastructure/repositories.py`
  - `src/api/dream-draw.ts`
  - `src/views/user/GenerateView.vue`
- 测试路径：
  - `tests/backend/test_prompt_polish.py`
  - `tests/backend/test_prompt_polisher.py`
  - `src/tests/generate-prompt-polish.spec.ts`
  - `tests/backend/test_admin_and_ops.py`
  - `tests/backend/test_gpt_image2_openai_compatible.py`
  - `tests/backend/test_integration_flows.py`
  - `tests/backend/test_user_flow.py`
- 文档路径：
  - `.adpp/changes/2026-05-18-guofeng-character-platform/prd.md`
  - `.adpp/changes/2026-05-18-guofeng-character-platform/design.md`
  - `.adpp/changes/2026-05-18-guofeng-character-platform/ux-notes.md`
  - `.adpp/changes/2026-05-18-guofeng-character-platform/test-report.md`
  - `.adpp/changes/2026-05-18-guofeng-character-platform/closeout-note.md`
  - `README.md`
- 归类结果：
  - API / schema / contract
  - backend behavior
  - frontend behavior / UX flow
  - docs
- 说明：
  - 当前工作区仍存在历史图片资产替换相关改动、测试生成的 `__pycache__/` 与 `backend/uploads/works/task-*` 文件，本轮未清理这些未跟踪产物。

## 3. 文档更新

### source_of_truth_docs

- `.adpp/changes/2026-05-18-guofeng-character-platform/prd.md`: 已更新 Prompt 润色能力、交互流程、数据需求和 `provider_id=chat` 约定。
- `.adpp/changes/2026-05-18-guofeng-character-platform/design.md`: 已更新 `/api/prompts/polish`、Prompt 润色后端调用链和密钥引用约定。
- `.adpp/changes/2026-05-18-guofeng-character-platform/ux-notes.md`: 已更新生成工作台 Prompt 区“润色”按钮、加载态和错误态。
- `.adpp/changes/2026-05-18-guofeng-character-platform/tasks.md`: 本轮未改；原任务清单已完成，本轮属于已完成生成工作台能力的增量补强。

### derived_docs

- `README.md`: 已同步当前实现范围、已验证链路和 `provider_id=chat` 配置说明。
- `.adpp/changes/2026-05-18-guofeng-character-platform/test-report.md`: 已追加本轮测试命令、结果和缺口。

## 4. 验证执行

- `python -m pytest tests/backend/test_prompt_polish.py -q`: 先红后绿，最终 `2 passed`。
- `npm.cmd run test -- src/tests/generate-prompt-polish.spec.ts`: 先红后绿，最终 `2 passed`。
- `python -m pytest tests/backend/test_prompt_polisher.py tests/backend/test_prompt_polish.py -q`: 通过，`5 passed`。
- `python -m pytest tests/backend -q`: 通过，`50 passed, 1 skipped`；跳过项为真实外部图像模型测试。
- `npm.cmd run test`: 通过，`7 files, 18 tests passed`。
- `npm.cmd run build`: 通过，`vue-tsc --noEmit && vite build` 成功。
- `npm.cmd run lint`: 未通过，项目未配置 `lint` 脚本。
- `GET http://127.0.0.1:5174/workspace`: 返回 `200`。

## 5. 证据

- `.adpp/changes/2026-05-18-guofeng-character-platform/test-report.md`: 本轮验证摘要。
- `dist/`: 前端生产构建产物已刷新。
- `coverage/`: 本轮未生成覆盖率 artifact。
- `test-results/`: 本轮未生成测试报告 artifact。
- `output/`: 本轮未新增 Prompt 润色截图或录屏证据。

## 6. 遗留风险与豁免

- `npm.cmd run lint` 失败原因是 `package.json` 缺少 `lint` 脚本，属于项目现有质量门禁缺口。
- 构建仍提示主 chunk 超过 500 kB，以及 `@vueuse/core` PURE 注释警告，属于既有构建优化问题。
- 浏览器 MCP 未暴露可用导航/截图工具，本轮只完成 HTTP 200 检查和组件测试验证。
- `provider_id=chat` 需要管理员在模型配置中心手动配置，且真实 API Key 建议通过 `env:KEY_NAME` 注入。

## 7. 下一步

- 人工确认 Prompt 润色文案与扩展方向是否符合产品调性。
- 补充 `lint` 脚本并纳入 ADPP 基础验证层。
- 后续可为 Prompt 润色增加风格/模板上下文参数，让扩展结果更贴合当前选择。
