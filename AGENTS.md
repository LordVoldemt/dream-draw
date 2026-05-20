<!-- ADPP-CODEX:START -->
## ADPP / Codex 工作流

- 优先读取 `.adpp/config.yaml`、`.adpp/spec/`、`.adpp/references/doc-closeout.md`
- 优先使用仓库自动发现的 repo skills：`$adpp-init`、`$adpp-prd`、`$adpp-design`、`$adpp-ux`、`$adpp-implement`、`$adpp-test`、`$adpp-deploy`、`$adpp-closeout`、`$adpp-status`
- 根据用户意图加载 `.adpp/skills/*.md`
- 如果用户直接输入“初始化项目 / 写 PRD / 系统设计 / 前端设计 / 编码实现 / 测试 / 部署 / 收口”，应优先匹配上述 ADPP repo skills
- 如果项目尚未初始化，但已运行 `adpp setup --target codex`，则回退读取 `.codex/adpp-skills/*.md`
- Codex 的 repo skill 自动发现目录为 `.agents/skills/`
- 初始化阶段的模板回退目录为 `.codex/adpp-templates/`
- 若用户要求“本轮完成”或“收口”，先执行 closeout 流程，再宣称完成
- Codex 侧的补充说明见 `.codex/ADPP-CODEX.md`
<!-- ADPP-CODEX:END -->

# Agent 工作规范 — 绘梦

本项目遵循 ADPP 范式。所有 agent 必须：

1. 编码前读取对应的 Plan 文档（`.adpp/changes/<feature>/tasks.md`）；若涉及前端界面，还需读取 `ux-notes.md`
2. 遵守 `.adpp/spec/` 中的规范
3. 不得执行危险操作（见 `.adpp/config.yaml` 中的 `danger_operations`）
4. 所有代码变更必须有对应测试
5. 声称“本轮完成”前，先执行 `/adpp:closeout`
6. 模型选择和密钥配置由外部运行环境管理，不写入项目配置
