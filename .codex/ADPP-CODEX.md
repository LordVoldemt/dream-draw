# ADPP Plugin — Codex Adapter

你是一个遵循 ADPP 范式的 Codex 工作代理。

## 核心规则

1. 写代码前先读取对应的规格文档；没有 PRD / Plan 不得直接生成业务代码。
2. 遇到人工门控节点必须暂停，等待用户明确确认。
3. 危险操作必须提前告知，不得静默执行。
4. 声称本轮完成前，必须先执行 closeout 流程。

## Skill 加载顺序

1. 优先使用仓库自动发现的 repo skills：`$adpp-init`、`$adpp-prd`、`$adpp-design`、`$adpp-ux`、`$adpp-implement`、`$adpp-test`、`$adpp-deploy`、`$adpp-closeout`
2. 优先读取 `.adpp/skills/*.md`
3. 如果项目尚未初始化，但已运行 `adpp setup --target codex`，则回退读取 `.codex/adpp-skills/*.md`
4. 初始化阶段优先使用 `.adpp/spec/`；若规范尚未生成，则回退读取 `.codex/adpp-templates/`

## 项目上下文

- 项目配置：`.adpp/config.yaml`
- 项目规范：`.adpp/spec/`
- 当前变更：`.adpp/changes/`
- 收口约束：`.adpp/references/doc-closeout.md`

如果缺少 `.adpp/skills/init.md` 且 `.codex/adpp-skills/init.md` 也不存在，应提示用户先运行 `adpp setup --target codex`。
