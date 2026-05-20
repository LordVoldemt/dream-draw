---
name: adpp-init
description: Use when initializing an ADPP project in Codex, or when the user asks to set up ADPP config, specs, CLAUDE.md, or AGENTS.md
---

# ADPP Init

读取并严格遵循 `.adpp/skills/init.md` 中定义的完整流程执行。

如果 `.adpp/skills/init.md` 不存在，则依次使用以下回退文件：

1. `.codex/adpp-skills/init.md`
2. 当前插件仓库中的 `skills/init.md`
