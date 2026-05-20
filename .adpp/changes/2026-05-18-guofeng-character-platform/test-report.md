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
