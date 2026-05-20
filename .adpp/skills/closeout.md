# ADPP Skill: 交付收口 (closeout)

## 触发条件
用户运行 `/adpp:closeout`，或描述"文档收口"、"同步文档"、"更新 progress"、"回写 PRD"、"记录验证证据"、"round closeout"、"本轮收尾"时激活。

---

## 核心目标

在声明"本轮完成"之前，完成以下动作：

1. 扫描本轮改动面
2. 映射必须更新的文档类型
3. 执行约定的验证命令
4. 记录验证证据
5. 生成 round closeout note

closeout 的优先顺序：

1. `source_of_truth_docs`
2. `derived_docs`
3. 证据与进度说明

不得用 progress note 或 closeout note 代替本该更新的 source-of-truth 文档。

---

## 前置检查

执行前必须读取：

- `.adpp/config.yaml`
- `.adpp/references/doc-closeout.md`（如果存在）
- `.adpp/changes/` 下当前进行中的变更
- 当前 worktree 状态（优先 `git status --short`、`git diff --name-only`）

如果 `.adpp/config.yaml` 不存在，停止并提示用户先运行 `/adpp:init`。

如果 `.adpp/config.yaml` 中缺少 `closeout` 配置，使用保守 fallback：

- `source_of_truth_docs`：当前 feature 目录下的 `prd.md`、`design.md`、`tasks.md`
- 如果本轮涉及前端界面：同时加入 `ux-notes.md`
- `derived_docs`：`README.md`、`docs/` 下与改动直接相关的说明文档
- `verification_layers.base`：根据技术栈选择最小验证命令
- `evidence_dirs`：`coverage/`、`test-results/`、`output/`、`.adpp/changes/{{ feature-dir }}/evidence/`

并在本轮 closeout note 中明确记录：`closeout 配置使用了 fallback，建议补齐项目级配置。`

如果 `.adpp/changes/` 下有多个未归档变更，默认选择最近修改且状态不是"已归档"的目录；若仍然歧义，再向用户确认。

---

## 强制流程

```
STEP 1: 读取项目级 closeout 策略
STEP 2: 扫描本轮改动面
STEP 3: 映射需要更新的文档
STEP 4: 执行验证命令
STEP 5: 记录证据
STEP 6: 生成 round closeout note
STEP 7: ▶ [人工确认] 完成本轮收口
```

---

## STEP 1：读取项目级 closeout 策略

从 `.adpp/config.yaml` 的 `closeout` 段读取：

- `source_of_truth_docs`
- `derived_docs`
- `trigger_matrix`
- `verification_layers`
- `evidence_dirs`
- `progress_note_template`

再读取 `.adpp/references/doc-closeout.md` 中的仓库级补充信息，重点关注：

- 哪些文档虽然看起来是历史文件，但实际上仍是有效事实来源
- 哪些文档是生成产物，不应手工编辑
- 哪些改动面需要额外验证
- 证据目录、命名约定和截图/报告保留要求
- round closeout note 是否需要同步到项目特定位置

输出当前策略摘要：

```markdown
📌 Closeout 策略摘要

当前变更：{{ feature_dir }}
source_of_truth_docs: {{ N }} 个
derived_docs: {{ N }} 个
trigger_matrix: {{ N }} 条
verification_layers: {{ N }} 层
evidence_dirs: {{ N }} 个
```

---

## STEP 2：扫描本轮改动面

优先执行：

```bash
git status --short
git diff --name-only
git diff --name-only --cached
```

如果当前目录不是 git 仓库，回退为：

1. 扫描 `.adpp/changes/{{ feature-dir }}/`
2. 读取最近修改的代码、配置、文档文件
3. 结合用户本轮目标构建 touched surface

必须把改动面归类到至少一个类别：

- API / schema / contract
- backend behavior
- frontend behavior / UX flow
- data / migration / script
- infra / deploy / CI
- docs-only
- evidence-only / review-only

输出改动面清单：

```markdown
📋 本轮改动面

- 代码路径：{{ paths }}
- 文档路径：{{ paths }}
- 配置路径：{{ paths }}
- 归类结果：{{ categories }}
- 是否存在未收口的文档改动：{{ yes/no }}
```

---

## STEP 3：映射需要更新的文档

使用 `trigger_matrix` 将改动面映射到必须更新的文档：

1. 先判断 `source_of_truth_docs`
2. 再判断 `derived_docs`
3. 最后再决定是否补充 progress / closeout note

映射时遵守以下规则：

- 改动影响事实边界、验收标准、接口、部署方式时，必须先更新 source-of-truth 文档
- generated docs 或派生产物只能在 source 文档完成后再同步
- 如果某类文档判断为"无需更新"，必须写出理由，不得静默跳过
- `.adpp/references/doc-closeout.md` 中标记为 live contract 的文件，按 source-of-truth 对待
- 如果本轮属于 `frontend behavior / UX flow`，同时检查 `.adpp/changes/{{ feature-dir }}/ux-notes.md` 是否需要同步更新

输出映射结果：

```markdown
🧭 文档映射结果

必须更新的 source docs:
- {{ path }}: {{ reason }}

必须更新的 derived docs:
- {{ path }}: {{ reason }}

本轮可不更新的 docs:
- {{ path }}: {{ reason }}
```

---

## STEP 4：执行验证命令

按以下顺序执行验证：

1. `verification_layers.base`
2. `trigger_matrix` 为当前改动面追加的验证
3. `verification_layers` 中更高层或发布层命令

执行规则：

- 不得声称"已验证"而不实际运行命令
- 如果用户明确说明是 docs-only 且没有行为变化，可只执行 docs-only 层或最小校验
- 如果命令不存在、环境缺失或执行失败，必须记录具体阻塞，不得假装通过
- 如果某个验证产生报告目录、覆盖率或截图，记入证据区

输出格式：

```markdown
🧪 验证执行结果

- {{ command }} -> ✅ / ❌ / 跳过
  说明：{{ summary }}
  产物：{{ artifact_paths 或 无 }}
```

如果关键验证失败，本轮 closeout 状态必须标记为 `未完成`。

---

## STEP 5：记录证据

从 `evidence_dirs` 中收集本轮证据：

- 测试报告
- 覆盖率报告
- E2E 截图或录像
- 构建日志
- 其他仓库约定的 artifact

记录证据时必须写清楚：

- 证据路径
- 对应命令
- 时间戳
- 证据说明

如果目录存在但无新证据，也必须写明"目录存在，但本轮无新增 artifact"。

---

## STEP 6：生成 round closeout note

生成或更新：

`.adpp/changes/{{ feature-dir }}/closeout-note.md`

文件至少包含以下章节：

```markdown
# Round Closeout: {{ feature_name }}

**日期**: {{ timestamp }}
**状态**: 待确认 / 已确认 / 未完成

## 1. 本轮范围
- {{ summary }}

## 2. 改动面扫描
- {{ touched_surface }}

## 3. 文档更新
### source_of_truth_docs
- {{ path }}: {{ action }}

### derived_docs
- {{ path }}: {{ action }}

## 4. 验证执行
- {{ command }}: {{ result }}

## 5. 证据
- {{ evidence_path }}: {{ note }}

## 6. 遗留风险与豁免
- {{ risk_or_waiver }}

## 7. 下一步
- {{ follow_up }}
```

如果 `progress_note_template` 存在，必须用它覆盖或增强第 1、4、5、6、7 节结构。

如果项目约定还需要回写进度文档、发布记录或额外 summary 文档，按 `.adpp/references/doc-closeout.md` 的规则同步更新。

---

## STEP 7：人工确认

closeout 完成后必须暂停并输出：

```markdown
▶ [人工确认] 本轮收口已完成，请确认：

  □ source-of-truth 文档已同步
  □ derived 文档已同步
  □ 验证已执行或已明确豁免原因
  □ 证据已记录
  □ closeout-note.md 已生成

closeout note:
  .adpp/changes/{{ feature-dir }}/closeout-note.md

输入：
  "确认收口" → 本轮可标记完成
  "补充：xxx" → 补完后重新 closeout
```

如果任一必需项未完成，不得对用户说"本轮已完成"。

---

## 禁止行为

| 禁止 | 原因 |
|---|---|
| 跳过改动面扫描直接写总结 | 容易漏文档和漏验证 |
| 用 progress note 代替 source-of-truth 文档 | 会造成事实源漂移 |
| 不跑命令只凭主观判断写"已验证" | 这是 closeout 最常见的失真来源 |
| 证据只写"见日志"不写路径 | 后续无法审计和复盘 |
| 有失败验证却仍声称收口完成 | 破坏 ADPP 的可追溯性 |
