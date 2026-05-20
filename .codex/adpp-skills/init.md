# ADPP Skill: 项目初始化 (init)

## 触发条件
用户运行 `/adpp:init` 或描述"初始化项目"、"setup"、"配置 AI 开发环境"时激活。

---

## 强制流程（不可跳过任何步骤）

```
STEP 1: 检查是否已初始化
STEP 2: 收集项目基本信息
STEP 3: 生成项目配置
STEP 4: 生成项目规范文档和 closeout 参考
STEP 5: 初始化目录结构
STEP 6: 生成 CLAUDE.md 和 AGENTS.md
STEP 7: 确认完成
```

---

## STEP 1：检查已有配置

检查 `.adpp/config.yaml` 是否存在：
- **存在** → 询问用户："检测到已有 ADPP 配置，是否重新初始化？（会覆盖现有配置）"
- **不存在** → 继续 STEP 2

如果当前项目中 `.adpp/skills/init.md` 还不存在，必须按以下顺序尝试回退：

1. `.claude/adpp-skills/init.md`
2. `.codex/adpp-skills/init.md`

如果两个回退文件都不存在，停止并提示用户先重新运行 `adpp setup`。

如果以下两个模板目录都不存在，或都缺少对应模板，也应停止并提示用户先运行 `adpp setup` 或 `adpp update`：

- `.claude/adpp-templates/`
- `.codex/adpp-templates/`

---

## STEP 2：收集项目基本信息

依次询问（每次一个问题）：

```
Q1: 项目名称是什么？
Q2: 项目类型？(Web应用 / 移动端 / 后端服务 / 数据平台 / 其他)
Q3: 主要技术栈？(例如：Python FastAPI + React + PostgreSQL)
Q4: 团队规模？(1人 / 2-5人 / 5人以上)
```

---

## STEP 3：生成项目配置

初始化阶段**不得**询问以下内容：

- 使用哪个模型
- 使用哪个 provider
- API Key / Token / Base URL
- 是否为 planning / coding / review 分阶段配置模型

这些内容应由用户自己的运行环境、Claude Code、oh-my-claudecode、环境变量或企业统一 AI 网关处理，而不是写入项目初始化流程。

生成的配置文件格式：
```yaml
# .adpp/config.yaml
project:
  name: "{{ project_name }}"
  type: "{{ project_type }}"
  tech_stack: "{{ tech_stack }}"
  team_size: "{{ team_size }}"
  created_at: "{{ timestamp }}"

runtime:
  model_management: "external"
  credentials_source: "user-environment"
  notes:
    - "模型选择由用户在 Claude Code 或外部插件中自行决定"
    - "密钥建议通过环境变量、oh-my-claudecode 或企业统一网关管理"

danger_operations:
  mode: "confirm"  # confirm | silent | mobile
  mobile_webhook: ""  # 企业微信/钉钉 webhook URL
  patterns:
    - "DROP TABLE"
    - "DELETE FROM"
    - "rm -rf"
    - "truncate"
    - "UPDATE.*WHERE.*1=1"

closeout:
  source_of_truth_docs:
    - ".adpp/changes/<feature>/prd.md"
    - ".adpp/changes/<feature>/design.md"
  derived_docs:
    - "README.md"
  trigger_matrix:
    - name: "api-or-backend-change"
      paths:
        - "src/api/**"
        - "backend/**"
      update:
        - ".adpp/changes/<feature>/prd.md"
        - ".adpp/changes/<feature>/design.md"
        - "README.md"
      verify:
        - "npm test"
    - name: "frontend-flow-change"
      paths:
        - "src/**"
        - "app/**"
      update:
        - ".adpp/changes/<feature>/design.md"
        - ".adpp/changes/<feature>/ux-notes.md"
        - "README.md"
      verify:
        - "npm run test"
  verification_layers:
    base:
      - "npm run lint"
      - "npm test"
    docs_only:
      - "markdownlint README.md"
  evidence_dirs:
    - "coverage/"
    - "test-results/"
    - "output/"
  progress_note_template: |
    # Round Closeout
    ## Summary
    - Scope: {{ scope }}
    ## Docs Updated
    - {{ docs_updated }}
    ## Verification
    - {{ verification_summary }}
    ## Evidence
    - {{ evidence_paths }}
    ## Risks
    - {{ risks }}
```

---

## STEP 4：生成项目规范文档和 closeout 参考

生成规范时必须优先读取并使用已安装目标中的内置模板，而不是从零自由发挥：

- `.claude/adpp-templates/coding-standards/default.md` 或 `.codex/adpp-templates/coding-standards/default.md`
- `.claude/adpp-templates/doc-standards/default.md` 或 `.codex/adpp-templates/doc-standards/default.md`
- `.claude/adpp-templates/test-standards/default.md` 或 `.codex/adpp-templates/test-standards/default.md`
- `.claude/adpp-templates/references/doc-closeout.md` 或 `.codex/adpp-templates/references/doc-closeout.md`
- `.claude/adpp-templates/references/ux-notes.md` 或 `.codex/adpp-templates/references/ux-notes.md`

生成原则：

1. 以内置模板为骨架，保留其核心质量门槛
2. 根据 `project.type`、`project.tech_stack` 对示例和细节做小幅定制
3. 不得删除模板中的核心规范条目，只能补充或细化
4. 若项目已有存量约定，可在模板基础上增加“项目特例”章节

基于技术栈，在 `.adpp/spec/` 下生成以下文件：

### coding-standards.md 模板结构
```markdown
# 编码规范 — {{ project_name }}

## 命名规范
## 注释规范  
## 禁止模式（Anti-patterns）
## 目录结构规范
## 错误处理规范
## 日志规范
```

### doc-standards.md 模板结构
```markdown
# 文档规范 — {{ project_name }}

## PRD 文档格式
## API 文档规范
## 注释要求
## CHANGELOG 格式
```

### test-standards.md 模板结构
```markdown
# 测试规范 — {{ project_name }}

## 测试分层（单元/集成/E2E）
## 覆盖率要求（≥80%）
## 测试文件命名规范
## Mock 规范
## 禁止在测试中做的事
```

同时生成 `.adpp/references/doc-closeout.md`，放置仓库级 closeout 定制内容：

### doc-closeout.md 模板结构
```markdown
# Closeout Reference — {{ project_name }}

## 1. Source Of Truth Docs
- 哪些文档必须和代码同轮更新

## 2. Derived Docs
- 哪些文档/生成物由 source docs 派生

## 3. Trigger Matrix Notes
- 哪类改动触发哪些文档和验证

## 4. Verification Layers
- 必跑命令
- 可按条件追加的命令
- 可豁免的 docs-only 场景

## 5. Evidence Directories
- 测试报告、截图、覆盖率、构建日志存放路径

## 6. Progress / Closeout Note Convention
- round closeout note 命名方式
- 是否需要同步 progress / release note
```

内置模板中已经预置以下主流工程规范基线，生成时应尽量保留：

- Conventional Commits
- Semantic Versioning
- Keep a Changelog
- Twelve-Factor App
- OWASP ASVS / OWASP Top 10

生成后必须输出：
```
▶ [人工确认] 请检查以下生成的规范文档，确认无误后输入 "确认" 继续：
  - .adpp/spec/coding-standards.md
  - .adpp/spec/doc-standards.md
  - .adpp/spec/test-standards.md
  - .adpp/references/doc-closeout.md
```

---

## STEP 5：初始化目录结构

创建以下目录和文件：
```
.adpp/
├── config.yaml          ← 项目配置
├── skills/              ← Skill 文件（从 .claude/adpp-skills/ 或 .codex/adpp-skills/ 复制）
│   ├── init.md
│   ├── prd.md
│   ├── design.md
│   ├── ux.md
│   ├── implement.md
│   ├── test.md
│   ├── deploy.md
│   └── closeout.md
├── spec/                ← 项目规范（已在 STEP 4 生成）
├── references/          ← 项目级补充参考
│   └── doc-closeout.md
├── changes/             ← 每次变更的文档
│   └── YYYY-MM-DD-feature-name/
│       ├── prd.md
│       ├── design.md
│       ├── ux-notes.md
│       ├── tasks.md
│       ├── test-report.md
│       ├── deploy-record.md
│       └── closeout-note.md
└── workspace/           ← 开发者 journal，跨 session 记忆

.gitignore 追加：
  .adpp/workspace/       ← 个人 journal 不提交
```

---

## STEP 6：生成上下文入口文件

**CLAUDE.md**（项目根目录）：
```markdown
# {{ project_name }} — ADPP 项目

> 本项目使用 ADPP 范式开发。AI 助手请优先读取根目录 CLAUDE.md，并结合以下内容获取完整工作流规则：
> .adpp/spec/、.adpp/workspace/current-phase.md、.adpp/references/doc-closeout.md

技术栈：{{ tech_stack }}
当前阶段：见 .adpp/workspace/current-phase.md
```

**AGENTS.md**（项目根目录，供 Codex 等其他 agent 读取）：
```markdown
# Agent 工作规范 — {{ project_name }}

本项目遵循 ADPP 范式。所有 agent 必须：
1. 编码前读取对应的 Plan 文档（.adpp/changes/<feature>/tasks.md）；若涉及前端界面，还需读取 ux-notes.md
2. 遵守 .adpp/spec/ 中的规范
3. 不得执行危险操作（见 .adpp/config.yaml 中的 danger_operations）
4. 所有代码变更必须有对应测试
5. 声称"本轮完成"前，先执行 `/adpp:closeout`
6. 模型选择和密钥配置由外部运行环境管理，不写入项目配置
```

---

## STEP 7：完成确认

输出初始化完成摘要：
```
✅ ADPP 初始化完成！

项目：{{ project_name }}
技术栈：{{ tech_stack }}
模型与凭据：外部管理（Claude Code / oh-my-claudecode / 环境变量）

已创建：
  .adpp/config.yaml
  .adpp/spec/coding-standards.md
  .adpp/spec/doc-standards.md
  .adpp/spec/test-standards.md
  .adpp/references/doc-closeout.md
  CLAUDE.md
  AGENTS.md

下一步：
  运行 /adpp:prd 开始需求分析
  运行 /adpp:status 查看项目状态
  如果当前使用 Codex，则按 AGENTS.md 指引进入 PRD 阶段
```

---

## 禁止行为

| 禁止 | 原因 |
|---|---|
| 跳过规范文档生成 | 规范是后续所有阶段的基础 |
| 不询问直接使用默认配置 | 团队需要确认规范内容 |
| 在初始化阶段询问或写入 API Key / Token | 密钥不应进入项目配置 |
| 初始化失败后不报告具体错误 | 用户无法排查问题 |
