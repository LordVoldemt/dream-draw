# /adpp:status

显示当前项目的 ADPP 开发状态。

执行以下检查并输出结果：

1. 读取 `.adpp/workspace/current-phase.md`，显示当前阶段
2. 读取 `.adpp/changes/` 目录，列出所有进行中的变更及状态
3. 检查当前分支和 git 状态
4. 显示待处理的危险操作（`.adpp/workspace/pending-approvals.log`，如果存在）

输出格式：
```
📋 ADPP 项目状态
================

项目：{{ name }}（来自 .adpp/config.yaml）
当前阶段：{{ phase }}
主力模型：{{ model }}

进行中的变更：
  {{ feature }}: {{ 当前状态 }} → 下一步: {{ next_action }}

待审批的危险操作：{{ N }} 条
  运行 /adpp:review-pending 查看详情
```
