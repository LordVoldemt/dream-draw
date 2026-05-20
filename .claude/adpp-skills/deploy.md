# ADPP Skill: CI/CD 部署 (deploy)

## 触发条件
用户运行 `/adpp:deploy` 或描述"部署"、"发布"、"上线"、"CI/CD"时激活。

---

## 前置检查

```
必须通过：
  ✅ 测试报告已确认（.adpp/changes/*/test-report.md 状态=已确认）
  ✅ Code Review 已通过
  ✅ 高危安全问题数量 = 0
```

---

## 强制流程

```
STEP 1: 确认部署环境和策略
STEP 2: 生成部署配置文件
STEP 3: ▶ [人工门控] 生产部署确认（生产环境专属）
STEP 4: 执行部署流水线
STEP 5: 灰度验证
STEP 6: 归档部署记录
```

---

## STEP 1：确认部署策略

```
📋 部署配置确认：

目标环境：dev / staging / production
部署策略：
  1) 直接部署（dev/staging 推荐）
  2) 蓝绿部署
  3) 灰度发布（生产推荐，先 10% 流量）
  4) 金丝雀发布

回滚策略：
  上一个稳定版本：{{ git tag }}
  回滚命令：{{ 自动生成 }}

选择部署策略：
```

---

## STEP 2：生成部署配置文件

基于 `.adpp/config.yaml` 中的技术栈，生成对应配置：

### Docker

```dockerfile
# 生成 Dockerfile（如不存在）
FROM {{ base_image }}
WORKDIR /app
COPY . .
RUN {{ install_command }}
EXPOSE {{ port }}
CMD {{ start_command }}
```

### Kubernetes

```yaml
# 生成 k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ app_name }}
spec:
  replicas: {{ replicas }}
  selector:
    matchLabels:
      app: {{ app_name }}
  template:
    spec:
      containers:
      - name: {{ app_name }}
        image: {{ image }}
        resources:
          limits:
            cpu: "{{ cpu }}"
            memory: "{{ memory }}"
```

### GitHub Actions

```yaml
# 生成 .github/workflows/deploy.yml
name: Deploy {{ app_name }}
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: {{ test_command }}
      - name: Build
        run: {{ build_command }}
      - name: Deploy
        run: {{ deploy_command }}
```

### GitLab CI

```yaml
# 生成 .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

test:
  script: {{ test_command }}
  coverage: '/TOTAL.*\s+([\d.]+)%/'

deploy:
  script: {{ deploy_command }}
  only: [main]
  when: manual  # 生产环境需要手动触发
```

---

## STEP 3：人工门控 — 生产部署确认

**仅限生产环境。必须暂停并输出**：

```
🔴 [生产部署确认] 即将部署到生产环境！

变更摘要：
  功能：{{ feature_name }}
  版本：{{ version }}
  变更文件：{{ N }} 个
  数据库迁移：{{ 有/无 }}

风险评估：
  影响范围：{{ 分析影响的用户/功能 }}
  数据变更：{{ 是否有不可逆的数据变更 }}
  预估停机时间：{{ N }} 分钟（{{ 0 = 零停机 }}）

回滚预案：
  回滚版本：{{ tag }}
  回滚命令：{{ command }}
  预计回滚时间：{{ N }} 分钟

{{ 如果有数据库迁移 }}：
  ⚠️ 本次部署包含数据库迁移，请确认：
  □ 迁移脚本已在 staging 环境验证
  □ 回滚 SQL 已准备好
  □ 数据已备份

输入 "确认部署 production" 继续（完整输入，防止误触发）
输入 "中止" 取消
```

---

## STEP 4：执行部署流水线

```
🚀 开始部署...

[1/5] 构建镜像...          ✅
[2/5] 运行 CI 测试...       ✅ ({{ N }} tests passed)
[3/5] 推送镜像...           ✅
[4/5] 更新 Kubernetes...    ✅
[5/5] 健康检查...           {{ 等待中... }}

健康检查 URL: {{ health_check_url }}
等待实例就绪...
```

---

## STEP 5：灰度验证

```
📊 灰度验证（流量：10%）

监控指标（5分钟观察期）：
  错误率：{{ N }}%  {{ <1% ? "✅" : "⚠️" }}
  P99 响应时间：{{ N }}ms  {{ <500ms ? "✅" : "⚠️" }}
  CPU 使用率：{{ N }}%
  内存使用率：{{ N }}%

{{ 如果指标正常 }}：
  ✅ 灰度验证通过，是否扩大到 100% 流量？
  "全量" → 推送到所有实例
  "继续观察" → 再等 5 分钟

{{ 如果指标异常 }}：
  ❌ 检测到异常：{{ 异常描述 }}
  建议立即回滚！

  执行回滚？
  "回滚" → 立即回滚到 {{ previous_version }}
  "忽略" → 接受风险，继续（不推荐）
```

---

## STEP 6：归档部署记录

生成 `.adpp/changes/{{ feature-dir }}/deploy-record.md`：

```markdown
# 部署记录: {{ 功能名称 }}

**部署时间**: {{ timestamp }}
**部署版本**: {{ version }}
**部署环境**: {{ env }}
**部署人员**: {{ user }}
**状态**: 成功/失败/回滚

---

## 部署详情

| 项目 | 内容 |
|---|---|
| 镜像版本 | {{ image_tag }} |
| 部署策略 | {{ strategy }} |
| 停机时间 | {{ N }} 分钟 |
| 数据库迁移 | 有/无 |

## 灰度结果

| 指标 | 基线 | 灰度期间 | 状态 |
|---|---|---|---|
| 错误率 | {{ N }}% | {{ N }}% | ✅/⚠️ |
| P99 延迟 | {{ N }}ms | {{ N }}ms | ✅/⚠️ |

## 回滚信息（备用）

```bash
{{ 完整回滚命令 }}
```
```

更新 `.adpp/workspace/current-phase.md`：
```markdown
当前阶段: 部署完成
部署版本: {{ version }}
部署时间: {{ timestamp }}
状态: ✅ 线上运行
下一步: 运行 /adpp:closeout

如需回滚：{{ 回滚命令 }}
```

---

## 禁止行为

| 禁止 | 原因 |
|---|---|
| 未经测试确认就部署 | 质量门控不可跳过 |
| 生产部署不经人工确认 | 生产是最关键的人工门控 |
| 灰度异常不回滚 | 用户体验和数据安全优先 |
| 部署时无回滚方案 | 凡事有备无患 |
| 数据库迁移前不备份 | 数据不可逆操作必须有备份 |
