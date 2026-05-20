---
name: adpp-status
description: Use when the user wants to inspect current ADPP phase, in-progress changes, or pending approvals in a Codex project
---

# ADPP Status

显示当前项目的 ADPP 开发状态。

优先读取：

- `.adpp/workspace/current-phase.md`
- `.adpp/changes/`
- `.adpp/workspace/pending-approvals.log`
- `.adpp/config.yaml`

如果 `.adpp/` 尚不存在，提示用户先运行 `$adpp-init` 或执行 `adpp setup` 后完成初始化。
