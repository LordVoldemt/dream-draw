# 测试报告: 垂直型 AI 国风角色生成平台

**测试日期**: 2026-05-20  
**测试人员**: AI（Codex）+ 人工确认  
**状态**: 待确认

---

## 测试结果摘要

| 测试类型 | 通过 | 失败 | 跳过 | 覆盖率 |
|---|---:|---:|---:|---:|
| 前端单元/组件测试 | 11 | 0 | 0 | 未生成 |
| 后端单元/集成测试 | 30 | 0 | 0 | 未生成 |
| 构建验证 | 1 | 0 | 0 | - |
| 联调验证 | 3 | 0 | 0 | - |
| 安全审计 | 0 | 1 | 1 | - |

说明：
- 前端 `vitest` 全部通过。
- 后端 `pytest` 全部通过。
- 前端生产构建通过。
- 本地联调已验证 `5173 -> 8000` 的 `/api` 代理生效，短信发送与登录链路可用。
- 当前未生成覆盖率报告，无法确认是否达到 `>=80%` 目标。
- 当前未引入浏览器级 E2E 自动化。

---

## 本轮执行范围

本轮重点覆盖：

- 注册页新增后的前端可用性
- 登录页到注册页跳转
- Vite 开发代理修复
- 手机号验证码发送与登录联调
- 已有后端主链路、风控与后台接口回归

---

## 实际执行命令

- `npm run test`
  - 结果：`3 files, 11 tests passed`
- `python -m pytest tests/backend -q`
  - 结果：`30 passed`
- `npm run build`
  - 结果：通过
- `python -m pip_audit -r backend/requirements.txt`
  - 结果：发现 3 条依赖漏洞
- `npm audit --omit=dev --json`
  - 结果：执行失败，当前镜像源不支持安全审计接口

---

## 联调验证

已实际验证：

- `GET http://127.0.0.1:5173`
  - 返回 `200`
- `GET http://127.0.0.1:8000/health`
  - 返回 `{"status":"ok"}`
- `POST http://127.0.0.1:5173/api/auth/sms/send-code`
  - 返回成功，包含开发环境验证码
- `POST http://127.0.0.1:5173/api/auth/login`
  - 返回成功，首次登录可获得新手积分

说明：
- 本地开发环境验证码当前为 `123456`
- 前端请求已不再错误落到 `5173` 静态资源路径，而是正确代理到 `8000`

---

## 验收标准覆盖情况

| 验收标准 | 对应用例/验证 | 状态 |
|---|---|---|
| 用户可完成一次登录-生成-查看-下载的完整流程 | `tests/backend/test_integration_flows.py::test_user_full_flow_home_login_generate_result_download` | 通过 |
| 生成后可分享并形成回流闭环 | `tests/backend/test_integration_flows.py::test_share_referral_flow_generates_link_and_new_user_can_complete_first_generation` | 通过 |
| 管理员可登录并维护用户/模型 | `tests/backend/test_integration_flows.py::test_admin_full_flow_login_users_detail_providers_monitoring` | 通过 |
| 游客禁止直接生成 | `tests/backend/test_guardrails.py::test_guest_cannot_generate` | 通过 |
| 新用户每日次数限制有效 | `tests/backend/test_guardrails.py::test_daily_limit_blocks_after_twenty_requests` | 通过 |
| IP 限流有效 | `tests/backend/test_guardrails.py::test_ip_rate_limit_blocks_frequent_requests` | 通过 |
| 重复 Prompt 防刷有效 | `tests/backend/test_guardrails.py::test_duplicate_prompt_is_blocked` | 通过 |
| 主模型异常时可切备用模型 | `tests/backend/test_guardrails.py::test_fallback_provider_is_used_when_primary_is_unavailable` | 通过 |
| 失败或拦截任务会退款 | `tests/backend/test_admin_and_ops.py::test_worker_refunds_failed_or_blocked_tasks` | 通过 |
| 注册页可走手机号验证码链路 | 本地联调手工验证 | 通过 |
| 登录页/注册页 API 请求可正确代理到后端 | 本地联调手工验证 | 通过 |

---

## 安全审计结果

| 风险等级 | 数量 | 说明 |
|---|---:|---|
| 高危 | 0 | 未单独识别高危项 |
| 中危 | 0 | 未单独识别中危项 |
| 低危 | 0 | 未单独识别低危项 |
| 已发现且必须处理 | 3 | `pip-audit` 已确认真实依赖漏洞 |

### Python 依赖漏洞

| 包 | 当前版本 | 风险 ID | 修复版本 |
|---|---|---|---|
| `pytest` | `8.3.5` | `CVE-2025-71176` | `9.0.3` |
| `starlette` | `0.46.2` | `CVE-2025-54121` | `0.47.2` |
| `starlette` | `0.46.2` | `CVE-2025-62727` | `0.49.1` |

### Node 审计阻塞

- 当前 `npm` registry 为 `https://registry.npmmirror.com`
- 该镜像不支持 `/-/npm/v1/security/*`
- 因此 `npm audit` 无法得到有效结果

### 代码层快速检查

- 后端仓库使用 `sqlite3` 参数化查询，快速检索未发现明显字符串拼接 SQL 执行
- 已有鉴权、越权、限流、重复提交、失败退款等专项测试
- 仍未补充浏览器侧 XSS/E2E 自动化验证

---

## 当前缺口

- [ ] 缺少覆盖率报告
- [ ] 缺少浏览器级 E2E 自动化
- [ ] `package.json` 未配置 `lint` 脚本，无法满足 `.adpp/config.yaml` 的基础验证层
- [ ] Python 依赖存在已知漏洞，需升级后回归
- [ ] Node 依赖安全审计受镜像源限制，需切换支持审计的 registry 后复查

---

## 测试环境

- 操作系统：Windows
- 前端：Vue 3 + Vite 7
- 后端：Python 3.11.2 + FastAPI
- 前端测试框架：Vitest 3.2.4
- 后端测试框架：Pytest 8.3.5
- 本地前端地址：`http://127.0.0.1:5173`
- 本地后端地址：`http://127.0.0.1:8000`

---

## 门禁结论

功能验证通过，但 ADPP 质量门禁未完全通过。

当前可以确认：

- 功能主链路可用
- 注册页与登录链路可用
- 开发联调环境已恢复正常

当前不能宣称“测试完全完成”的原因：

- 依赖安全漏洞未处理
- `npm audit` 未完成
- 覆盖率报告缺失
- `lint` 脚本缺失

建议下一步：

1. 升级 `pytest` 与 `starlette`
2. 补充 `lint` 脚本
3. 切换 npm registry 后重新执行 `npm audit`
4. 视需要补 Playwright E2E 与覆盖率报告

---

## 2026-05-23 首页与生成页图片资产补充验证

### 本轮范围

- 将 `HomeView.vue` 首页所有远程 Unsplash 展示图替换为本地生成图片资产。
- 将 `GenerateView.vue` 生成工作台风格卡与右侧预览图替换为同一套本地风格资产。
- 新增测试约束，防止上述页面重新引入远程占位图片。

### 实际执行命令

- `npm.cmd run test -- home-carousel generate-assets`
  - 结果：`2 files, 4 tests passed`
- `npm.cmd run test`
  - 结果：`6 files, 16 tests passed`
- `npm.cmd run build`
  - 结果：通过，`vue-tsc --noEmit && vite build` 成功
- 浏览器烟测：`http://127.0.0.1:5174/`
  - 结果：首页 `13` 张图片全部加载成功，断图数 `0`，远程展示图数 `0`
- 浏览器烟测：`http://127.0.0.1:5174/workspace`
  - 结果：生成工作台 `7` 张图片全部加载成功，断图数 `0`，远程展示图数 `0`

### 证据

- `output/home-assets-final-contact-sheet.jpg`
  - 说明：本轮首页与生成页复用的本地图片资产预览拼图
- 原始生成图片目录：
  - `C:\Users\jarvis\.codex\generated_images\019e5045-2c02-7f92-800e-8aef4149dc04`

### 备注

- `GenerateView.vue` 中仍保留 `https://example.com/reference-*.png`，它是提交生成任务时模拟参考图 URL 的请求数据，不是页面图片 `src` 展示资源。
- 构建仍有 Vite/Rollup chunk size warning，与本次图片替换无直接关系，不阻塞本轮验证。

---

## 2026-05-23 生成工作台 Prompt 润色验证

### 本轮范围

- 在生成工作台 Prompt 区新增“润色”按钮，支持加载态、未登录跳转、空输入/超长输入提示和失败提示。
- 新增 `POST /api/prompts/polish`，后端读取 `model_providers.provider_id = 'chat'` 的 OpenAI-compatible chat provider 调用 `chat/completions`。
- `api_key_ref` 支持直接密钥或 `env:KEY_NAME` 环境变量引用。
- 恢复重复 Prompt 防刷校验，修复后端测试中异步任务状态断言的竞态。
- 将真实联网图像模型测试改为 `RUN_GPT_IMAGE2_OPENAI_COMPATIBLE_TESTS=1` 时才启用，避免常规回归误触外部服务。

### 实际执行命令

- `python -m pytest tests/backend/test_prompt_polish.py -q`
  - RED：接口未实现时 `2 failed`
  - GREEN：实现后 `2 passed`
- `npm.cmd run test -- src/tests/generate-prompt-polish.spec.ts`
  - RED：按钮未实现时 `2 failed`
  - GREEN：实现后 `2 passed`
- `python -m pytest tests/backend/test_prompt_polisher.py tests/backend/test_prompt_polish.py -q`
  - 结果：`5 passed`
- `python -m pytest tests/backend -q`
  - 结果：`50 passed, 1 skipped`
  - 跳过项：真实外部图像模型调用测试，默认按环境变量开关跳过
- `npm.cmd run test`
  - 结果：`7 files, 18 tests passed`
- `npm.cmd run build`
  - 结果：通过，`vue-tsc --noEmit && vite build` 成功
- `npm.cmd run lint`
  - 结果：失败，`package.json` 未配置 `lint` 脚本
- 页面可用性检查：`GET http://127.0.0.1:5174/workspace`
  - 结果：`200`

### 证据

- 新增后端测试：
  - `tests/backend/test_prompt_polish.py`
  - `tests/backend/test_prompt_polisher.py`
- 新增前端测试：
  - `src/tests/generate-prompt-polish.spec.ts`
- 文档同步：
  - `README.md`
  - `.adpp/changes/2026-05-18-guofeng-character-platform/prd.md`
  - `.adpp/changes/2026-05-18-guofeng-character-platform/design.md`
  - `.adpp/changes/2026-05-18-guofeng-character-platform/ux-notes.md`

### 备注

- 构建仍有既有 Vite/Rollup chunk size warning，与本轮 Prompt 润色无直接关系。
- `npm.cmd run test` 和 `npm.cmd run build` 均输出 `npm warn Unknown user config "sass_binary_site"`，不影响命令结果。
- 本轮未生成覆盖率报告，也未完成浏览器截图证据；当前环境只完成了 `/workspace` HTTP 200 检查和组件测试覆盖。
