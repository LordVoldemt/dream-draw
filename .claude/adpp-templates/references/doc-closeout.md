# Closeout Reference — {{ project_name }}

> 这是项目级 closeout 参考模板。请在初始化后按仓库实际情况填写，作为 `/adpp:closeout` 的语义补充层。

---

## 1. Source Of Truth Docs

列出必须与代码同轮更新的事实源文档，例如：

- `docs/product/prd.md`
- `docs/architecture/system-design.md`
- `openapi/openapi.yaml`
- `deploy/README.md`

说明：

- 哪些文档是强制同步
- 哪些文件虽然带历史日期，但仍是活文档
- 哪些生成文件不允许手工修改

---

## 2. Derived Docs

列出由事实源派生的文档和产物，例如：

- `README.md`
- `docs/user-guide.md`
- SDK / generated client
- QA matrix

---

## 3. Trigger Matrix Notes

按改动面说明 closeout 应触发哪些文档与验证：

- API / schema 变化
- 前端交互变化
- 部署方式变化
- 权限与安全策略变化
- 仅文档变更

建议写明：

- 命中条件
- 必须更新的文档
- 必跑命令
- 可接受的豁免条件

---

## 4. Verification Layers

### Base

- 每轮都要跑的基础验证

### Module-specific

- 仅在某类改动命中时追加的验证

### Release / Deployment

- 发布前或灰度阶段才执行的验证

---

## 5. Evidence Directories

列出本项目实际证据路径，例如：

- `coverage/`
- `test-results/`
- `playwright-report/`
- `output/verification/`
- `artifacts/`

并说明：

- 哪些目录由哪些命令产出
- 哪些截图、录像、日志必须保留

---

## 6. Progress / Closeout Note Convention

说明本项目对以下内容的约定：

- closeout note 文件命名
- progress note 是否必需
- 发布记录位置
- 是否要求在 MR / PR 中粘贴验证摘要
- 是否要求附截图、报告链接或环境说明
