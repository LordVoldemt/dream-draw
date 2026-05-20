# ADPP Skill: 前端设计 (ux)

## 触发条件
用户运行 `/adpp:ux`，或描述"前端设计"、"UX 设计"、"页面设计"、"交互设计"、"Figma"、"Stitch"、"设计稿落地"时激活。

---

## 前置检查

```
必须存在且已确认：
  ✅ .adpp/changes/*/prd.md（状态=已确认）
  ✅ .adpp/changes/*/design.md（状态=已确认）

建议存在：
  ◇ .claude/adpp-templates/references/ux-notes.md 或 .codex/adpp-templates/references/ux-notes.md
```

如果 `design.md` 尚未确认，停止并提示用户先运行 `/adpp:design` 完成系统设计。

如果读取 PRD 和 `design.md` 后，判断当前变更不涉及前端页面、交互流程、组件、视觉样式或响应式要求，则停止并提示：

```text
当前变更未检测到明确的前端设计范围，可跳过 /adpp:ux，直接按系统设计进入实现阶段。
```

---

## 强制流程

```
STEP 1: 识别前端范围与设计输入
STEP 2: 生成或更新 ux-notes.md
STEP 3: 检查设计稿可访问性与缺口
STEP 4: ▶ [人工门控] UX 设计评审
STEP 5: 基于 design.md + ux-notes.md 生成 unified tasks.md
STEP 6: 归档与阶段流转
```

---

## STEP 1：识别前端范围与设计输入

读取：

- `.adpp/changes/{{ feature-dir }}/prd.md`
- `.adpp/changes/{{ feature-dir }}/design.md`
- `.adpp/changes/{{ feature-dir }}/ux-notes.md`（如果已存在）
- `.claude/adpp-templates/references/ux-notes.md` 或 `.codex/adpp-templates/references/ux-notes.md`（如果存在）

提取并输出：

- 涉及的页面 / 模块
- 主要用户角色
- 关键交互流程
- 需要新增或复用的组件
- 设计稿输入来源（Figma / Stitch / 截图 / 导出稿 / 纯文字说明）
- 当前是否具备“可直接进入实现”的设计输入

输出格式：

```markdown
🎨 前端设计范围识别

- 页面/模块：{{ pages }}
- 角色：{{ roles }}
- 关键流程：{{ flows }}
- 组件范围：{{ components }}
- 设计输入：{{ figma / stitch / screenshots / notes }}
- 设计完整度：{{ 足够 / 缺失 }}
```

---

## STEP 2：生成或更新 ux-notes.md

生成或更新：

`.adpp/changes/{{ feature-dir }}/ux-notes.md`

优先使用已安装目标中的 `ux-notes.md` 模板结构；如果模板不存在，则至少保证包含以下字段：

```markdown
# UX 设计要点: {{ feature_name }}

**基于系统设计**: {{ design.md 版本 }}
**状态**: 草稿 / 待评审 / 已确认

## 1. 变更范围
## 2. 设计输入总表
## 3. 页面级实现说明
## 4. 交互流程
## 5. 组件清单
## 6. 视觉约束
## 7. 表单与校验规则（如适用）
## 8. 响应式要求
## 9. 文案与语气
## 10. 实现注意事项
## 11. 交付前核对清单
```

填写要求：

- 不能只贴设计稿链接
- 每个页面至少要写页面用途、交互流程、组件清单、响应式要求
- 如果设计稿当前不可访问，必须补截图、导出稿或关键节点说明
- 如果一个功能涉及多个页面或多个设计节点，必须逐项写清映射关系

---

## STEP 3：检查设计稿可访问性与缺口

如果 `ux-notes.md` 中填写了设计稿链接：

- 当前运行环境能够访问并读取页面内容时，可将其作为实现输入
- 当前运行环境无法访问、需要额外登录、或只能看到空白/无权限页面时，不得声称“可以按设计稿实现”

此时必须把缺口归类为以下之一：

1. 链接存在，但当前环境不可访问
2. 链接可访问，但页面用途或节点映射不清
3. 仅有链接，没有截图或关键视觉说明
4. 缺少关键状态页（空态 / 错误态 / 加载态 / 成功态）

输出格式：

```markdown
🧩 设计输入缺口

- 缺口类型：{{ type }}
- 影响页面：{{ pages }}
- 是否阻塞实现：{{ yes/no }}
- 补充建议：{{ screenshot / export / annotation / rewrite notes }}
```

如果缺口会导致前端实现高度依赖猜测，必须在 UX 评审前提示用户补充。

---

## STEP 4：人工门控 — UX 设计评审

**必须暂停并输出**：

```text
▶ [UX 评审] 前端设计文档已生成：.adpp/changes/{{ feature-dir }}/ux-notes.md

UX 评审检查清单：
  □ 页面范围是否完整？
  □ 关键交互流程是否清楚？
  □ 组件新增/复用关系是否清楚？
  □ 视觉约束是否足够支持实现？
  □ 响应式要求是否清楚？
  □ 设计稿链接是否可访问？不可访问时是否已补截图/导出稿？
  □ 是否存在仍需产品/设计补充确认的点？

确认后输入：
  "确认UX" → 生成 tasks.md，进入编码阶段
  "修改：xxx" → 描述修改点
  "待补充：xxx" → 标记设计输入缺口，暂不继续
```

确认后，必须把 `ux-notes.md` 状态更新为 `已确认`。

---

## STEP 5：基于 design.md + ux-notes.md 生成 unified tasks.md

用户确认后，生成或覆盖：

`.adpp/changes/{{ feature-dir }}/tasks.md`

说明：

- 若当前 feature 为前端相关变更，`tasks.md` 以 `design.md` + `ux-notes.md` 为统一输入重新生成
- 不得继续沿用只基于系统设计生成的旧任务拆分

`tasks.md` 应尽量按以下阶段拆分：

```markdown
# 实现计划: {{ 功能名称 }}

**基于系统设计**: {{ design.md 版本 }}
**基于前端设计**: {{ ux-notes.md 版本 }}
**预估工时**: {{ N }} 小时
**拆分原则**: 每个任务编码量 ≤ 50 行，可独立测试

---

## 任务列表

### Phase 1: 数据与接口准备
- 后端依赖、接口对齐、数据结构准备

### Phase 2: 页面骨架与路由
- 页面容器、路由、布局、主区域搭建

### Phase 3: 核心组件与交互
- 表单、列表、弹窗、抽屉、状态切换、校验逻辑

### Phase 4: 视觉细节与响应式
- 空态 / 加载态 / 错误态 / 成功态
- 多端适配

### Phase 5: 集成与测试
- 单元测试
- 交互测试
- E2E / 可视化验证
```

如果后端与前端任务交织，必须显式写明依赖关系，不得让前端任务隐式依赖一个未声明完成的后端任务。

---

## STEP 6：归档与阶段流转

更新 `.adpp/workspace/current-phase.md`：

```markdown
当前阶段: 前端设计已确认，进入编码阶段
当前变更: .adpp/changes/{{ feature-dir }}/
系统设计状态: ✅ 已确认
UX 设计状态: ✅ 已确认
Plan 状态: ✅ 已生成（{{ N }} 个任务）
下一步: 运行 /adpp:implement
```

---

## 禁止行为

| 禁止 | 原因 |
|---|---|
| 只有设计稿链接，没有文字化设计约束 | 实现阶段极易因为权限或环境问题失真 |
| UX 未确认就生成最终 tasks.md | 前端任务拆分会偏离真实交互 |
| 只看 `design.md` 不读 `ux-notes.md` 就开始前端实现 | 系统设计无法覆盖细粒度页面行为 |
| 设计稿不可访问却声称“按稿实现” | 属于伪精确实现 |
| 前端任务不写响应式和状态页面 | 最容易在实现阶段被遗漏 |
