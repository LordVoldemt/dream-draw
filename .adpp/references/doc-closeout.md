# Closeout Reference — 绘梦

> 这是项目级 closeout 参考模板。请在初始化后按仓库实际情况填写，作为 `/adpp:closeout` 的语义补充层。

---

## 1. Source Of Truth Docs

当前项目默认以 ADPP 轮次文档作为事实源，必须与代码同轮更新：

- `.adpp/changes/<feature>/prd.md`
- `.adpp/changes/<feature>/design.md`
- `.adpp/changes/<feature>/tasks.md`
- `.adpp/changes/<feature>/ux-notes.md`（涉及前端交互时）

说明：

- `prd.md`、`design.md`、`tasks.md` 为强制同步文档
- `ux-notes.md` 在页面布局、交互、组件行为变化时强制同步
- 若后续引入 OpenAPI、部署文档或独立架构文档，应补入本节

---

## 2. Derived Docs

由事实源派生、需要按需同步的文档和产物：

- `README.md`
- 页面演示截图、测试报告、发布摘要
- 未来如引入 `openapi/` 生成产物、SDK 或用户手册，也应加入本节

---

## 3. Trigger Matrix Notes

### API / schema 变化

- 命中条件：Python 接口、请求参数、响应字段、鉴权逻辑变更
- 必须更新的文档：`prd.md`、`design.md`、`tasks.md`
- 必跑命令：`pytest`

### 前端交互变化

- 命中条件：Vue 页面结构、Element Plus 组件行为、表单流程、路由交互变更
- 必须更新的文档：`design.md`、`ux-notes.md`、`tasks.md`、`README.md`（如影响使用方式）
- 必跑命令：`npm run test`

### 部署方式变化

- 命中条件：构建方式、环境变量、运行命令、部署脚本变更
- 必须更新的文档：`design.md`、部署说明、`README.md`
- 必跑命令：对应构建/部署校验命令

### 权限与安全策略变化

- 命中条件：登录、鉴权、角色权限、文件上传、敏感操作策略变更
- 必须更新的文档：`prd.md`、`design.md`、`tasks.md`
- 必跑命令：受影响模块测试 + 安全验证

### 仅文档变更

- 命中条件：只改文档，不改业务代码
- 必须更新的文档：对应事实源或派生文档
- 可接受的豁免条件：可跳过业务测试，但需至少检查文档引用、命令和路径有效性

---

## 4. Verification Layers

### Base

- `npm run lint`
- `npm run test`
- `pytest`

### Module-specific

- 涉及前端页面时，追加组件测试、交互测试或 E2E
- 涉及 Python 接口或数据层时，追加集成测试
- 涉及上传、权限、安全策略时，追加专项安全验证

### Release / Deployment

- 发布前执行构建、冒烟验证和关键路径回归
- 若存在灰度环境，记录环境地址、版本号与验证结果

---

## 5. Evidence Directories

建议使用以下证据路径：

- `coverage/`
- `test-results/`
- `output/`
- `playwright-report/`（若后续引入 E2E）

并说明：

- 单元测试、集成测试、覆盖率报告优先落到上述目录
- 关键交互截图、构建日志、失败日志在 closeout 中附上相对路径
- 若某轮仅人工验证，也要记录验证步骤和截图路径

---

## 6. Progress / Closeout Note Convention

- closeout note 文件命名：`.adpp/changes/<feature>/closeout-note.md`
- test report 文件命名：`.adpp/changes/<feature>/test-report.md`
- deploy record 文件命名：`.adpp/changes/<feature>/deploy-record.md`
- 若一轮跨多次提交，建议同步维护 progress note
- MR / PR 中应粘贴验证摘要、风险说明和证据路径
- 涉及 UI 变更时，建议附页面截图或录屏说明
