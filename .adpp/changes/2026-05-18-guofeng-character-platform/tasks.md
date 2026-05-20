# 实施任务清单: 垂直型 AI 国风角色生成平台
**基于文档**:
- `D:\IDEA\github\dream-draw\.adpp\changes\2026-05-18-guofeng-character-platform\design.md`
- `D:\IDEA\github\dream-draw\.adpp\changes\2026-05-18-guofeng-character-platform\ux-notes.md`
- `D:\IDEA\github\dream-draw\.adpp\workspace\figma-mcp-results.json`

**状态**: 已完成  
**说明**:
- 本清单用于 `/adpp:implement` 阶段。
- 前端任务已按 `ux-notes.md` 页面定义和 `figma-mcp-results.json` 中已抓取的 Figma 页面/节点进行映射。
- 由于 Figma MCP 本轮存在调用限流，部分页面只有 UX 文本约束和 Figma 链接，没有完整节点元数据；这些任务已显式标注“待补充 Figma 细节”。
- 所有实现任务均需补充对应测试，遵守 TDD。

---

## 0. 实施原则

- 先完成后端基础设施、数据模型、鉴权与异步生成主链路，再落用户端页面和管理端页面。
- 前端实现必须严格对齐以下三层输入优先级：
  1. `tasks.md` 中的页面级任务
  2. `ux-notes.md` 中的枚举、状态、交互与响应式约束
  3. `figma-mcp-results.json` 中已拿到的 Figma 页面节点与结构线索
- 若 Figma 元数据缺失，不允许自由发挥业务元素；以 `ux-notes.md` 和 PRD 枚举为准完成首版。
- 每个页面任务都应覆盖：
  - 路由与页面骨架
  - 状态管理
  - API 接口对接
  - 空态/加载态/错误态
  - 单元测试或组件测试

---

## 1. 基础设施与工程骨架

- [x] `T001` 初始化后端项目结构，划分 `auth / users / points / generation / works / payments / admin / model_providers / monitoring` 模块
  - 产出: Python Web API 工程目录、配置加载、环境变量约定、基础异常处理中间件
  - 测试: 应用启动测试、配置加载测试

- [x] `T002` 初始化前端用户端与管理端应用骨架
  - 产出: Vue3 + Element Plus 路由、布局、API client、状态管理、权限守卫
  - 测试: 路由基础测试、鉴权守卫测试

- [x] `T003` 建立共享枚举与常量中心，统一 PRD 中的风格、模板、比例、质量档位、模型状态、任务状态
  - 必含枚举:
    - `style_tang_dynasty`
    - `style_han_dynasty`
    - `style_xianxia`
    - `style_new_chinese`
    - `style_gufeng_portrait`
    - `style_cinematic`
    - `tpl_oc_avatar`
    - `tpl_dreamgirl_portrait`
    - `tpl_novel_heroine`
    - `tpl_hanfu_photoshoot`
    - `tpl_wallpaper_character`
    - `tpl_xiaohongshu_cover`
    - `tpl_video_cover`
    - `tpl_character_sheet`
    - `ratio_square_1_1`
    - `ratio_portrait_3_4`
    - `ratio_portrait_2_3`
    - `ratio_landscape_4_3`
    - `ratio_landscape_16_9`
    - `ratio_vertical_9_16`
    - `standard`
    - `hd`
    - `ultra`
    - `healthy`
    - `degraded`
    - `unavailable`
    - `maintenance`
    - `pending`
    - `generating`
    - `reviewing`
    - `success`
    - `failed`
    - `blocked`
  - 测试: 枚举映射测试、前后端一致性测试

- [x] `T004` 建立对象存储、Redis、数据库、短信、支付、OpenAI-compatible 模型配置的环境配置抽象
  - 产出: 配置模型、依赖注入、provider adapter 基类
  - 测试: 配置解析测试、provider schema 校验测试

---

## 2. 数据模型与后端核心能力

- [x] `T005` 建立数据库 schema 与迁移脚本
  - 表范围:
    - `users`
    - `generation_tasks`
    - `works`
    - `point_transactions`
    - `payment_orders`
    - `share_events`
    - `favorites`
    - `model_providers`
    - `model_health_logs`
    - `admins`
  - 关键约束:
    - `users.phone` 唯一
    - 用户数据按 `user_id` 隔离
    - 模型配置支持多个 OpenAI-compatible provider
  - 测试: migration 测试、约束测试、索引存在性测试

- [x] `T006` 实现短信验证码登录与首登开户逻辑
  - 范围:
    - `POST /api/auth/sms/send-code`
    - `POST /api/auth/login`
  - 规则:
    - 仅手机号验证码登录
    - 首次登录自动创建账号
    - 首次登录赠送 10 次免费生成额度或等价值积分
  - 测试: 发送验证码、登录成功、验证码错误、首登开户、重复登录测试

- [x] `T007` 实现用户资料、积分余额与积分流水查询能力
  - 范围:
    - `GET /api/user/profile`
    - `GET /api/user/points`
  - 测试: 已登录查询、未登录拒绝、数据隔离测试

- [x] `T008` 实现风格、模板、灵感 Prompt 配置查询接口
  - 范围:
    - `GET /api/styles`
    - `GET /api/templates`
    - `GET /api/prompts/inspirations`
  - 规则:
    - 数据必须与 PRD / UX 枚举一致
    - 支持热门模板、最近爆款、小红书热门、汉服热门分组
  - 测试: 枚举完整性测试、筛选测试、返回结构测试

- [x] `T009` 实现积分报价服务
  - 范围:
    - `POST /api/generate/quote`
  - 输入字段:
    - `ratio_id`
    - `style_id`
    - `template_id`
    - `reference_image_url`
    - `reference_image_count`
    - `quality_level`
  - 计费要求:
    - 质量档:
      - `standard = 1`
      - `hd = 2`
      - `ultra = 3`
    - 参考图附加:
      - `0张 = +0`
      - `1张 = +1`
      - `2张 = +2`
      - `3张 = +3`
    - 比例当前阶段统一 `+0`
    - 风格与模板需要给出明确枚举附加值，并可在配置层维护
  - 产出:
    - 基础积分
    - 风格附加积分
    - 模板附加积分
    - 参考图附加积分
    - 最终积分
  - 测试: 各档位组合报价测试、边界输入测试、非法枚举测试

- [x] `T010` 实现生成任务创建与状态查询接口
  - 范围:
    - `POST /api/generate/tasks`
    - `GET /api/generate/tasks/{id}`
  - 规则:
    - 创建前检查登录、积分、限流、Prompt 合规
    - 状态机覆盖 `pending / generating / reviewing / success / failed / blocked`
  - 测试: 创建任务、状态流转、权限校验、积分不足、限流测试

- [x] `T011` 实现异步生成 worker 与模型 adapter 调用链
  - 范围:
    - Prompt 增强
    - 风格模板拼接
    - 参考图参数透传
    - 多 provider 路由
    - 失败重试与主备切换
  - 规则:
    - OpenAI-compatible 模型配置可动态切换
    - 主模型 `degraded` 或 `unavailable` 时切备
  - 测试: adapter 单测、路由测试、失败降级测试、超时重试测试

- [x] `T012` 实现生成后审核、积分扣减/退款、作品落库与 MinIO 存储
  - 规则:
    - 成功后扣减或确认消耗积分
    - 失败自动退款
    - 审核失败返回 `blocked`
  - 测试: 成功链路、失败退款、审核拦截、对象存储回写测试

- [x] `T013` 实现作品列表、作品详情、再次生成、分享素材生成接口
  - 范围:
    - `GET /api/works`
    - `GET /api/works/{id}`
    - `POST /api/works/{id}/share`
  - 测试: 用户数据隔离、列表筛选、分享 payload 测试

- [x] `T014` 实现支付订单与支付回调
  - 范围:
    - `POST /api/pay/orders`
    - `POST /api/pay/callback/{channel}`
  - 规则:
    - 支持微信支付与支付宝
    - 套餐固定为 `30/9.9`、`100/29.9`、`300/69.9`
  - 测试: 下单、重复回调、支付成功、支付失败、积分到账测试

- [x] `T015` 实现分享回流埋点与来源追踪
  - 范围:
    - 作品分享事件记录
    - 新用户回流来源绑定
  - 测试: 分享记录测试、回流归因测试

---

## 3. 管理后台后端能力

- [x] `T016` 实现管理员登录能力
  - 范围:
    - `POST /api/admin/login`
  - 测试: 登录成功、密码错误、禁用管理员测试

- [x] `T017` 实现用户管理与用户详情接口
  - 范围:
    - `GET /api/admin/users`
    - `GET /api/admin/users/{id}`
    - `PATCH /api/admin/users/{id}/points`
    - `PATCH /api/admin/users/{id}/status`
  - 规则:
    - 手机号脱敏
    - 危险操作需要原因字段与二次确认能力
  - 测试: 搜索、筛选、详情查询、积分调整、冻结解冻测试

- [x] `T018` 实现模型配置中心接口
  - 范围:
    - `GET/POST /api/admin/model-providers`
    - `PATCH /api/admin/model-providers/{id}`
    - `PATCH /api/admin/model-providers/{id}/status`
  - 规则:
    - `api_mode` 当前固定 `openai_compatible`
    - 支持主模型、备用模型、优先级、能力标签、QPS、超时配置
  - 测试: 新增、编辑、启停、字段校验、默认模型切换测试

- [x] `T019` 实现模型状态监控接口
  - 范围:
    - `GET /api/admin/model-monitoring`
  - 指标:
    - 在线状态
    - 成功率
    - 平均延迟
    - 超时次数
    - 失败次数
    - 审核拦截率
    - 当前排队任务数
  - 测试: 指标聚合测试、状态映射测试、空数据测试

---

## 4. 前端公共层任务

- [x] `T020` 建立用户端视觉基线与通用布局
  - 产出:
    - 顶部导航
    - 用户登录入口
    - 积分入口
    - 页面容器、卡片、按钮、状态提示样式
  - 依赖:
    - `T002`
    - `T003`
  - 测试: Layout 组件测试、导航态测试

- [x] `T021` 建立用户端生成相关共享组件
  - 组件范围:
    - Prompt 输入框
    - 风格卡片
    - 模板卡片
    - 比例选择器
    - 参考图上传器
    - 积分报价卡
    - 结果操作栏
  - 测试: 组件交互测试、props/render 测试

- [x] `T022` 建立管理端通用布局与表格/表单/状态卡组件
  - 组件范围:
    - AdminLayout
    - 数据表格工具栏
    - 右侧配置表单
    - 状态概览卡
    - 危险操作确认弹窗
  - 测试: 布局与交互测试

---

## 5. 用户端页面任务

### 5.1 首页

- [x] `T023` 实现首页页面骨架与首屏 Hero
  - 页面: 首页
  - Figma 来源:
    - 页面 URL: `https://www.figma.com/design/0oLoQWIykGOTIvvzeMsQan/%E7%A7%91%E7%A0%94%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0?node-id=29-3917&t=yow0lQYCugEsx1ml-11`
    - 节点: `29:3917`
    - MCP 状态: 已抓取元数据
  - 关键元素:
    - TopNavBar
    - Banner Hero
    - 主标题
    - 副标题
    - `立即生成` 主 CTA
    - `看看案例` 辅助 CTA
  - 依赖:
    - 无登录强依赖
  - 验收:
    - 游客可访问
    - 点击 CTA 可带预设参数跳生成工作台
  - 测试: 页面渲染测试、CTA 跳转测试

- [x] `T024` 实现首页风格展示区、情绪模板区、案例展示区
  - 页面: 首页
  - Figma 来源:
    - 节点: `29:3917`
    - 仅有 frame 元数据，细节按 `ux-notes.md` 落地
  - 关键元素:
    - 风格展示卡:
      - 盛唐
      - 汉代
      - 仙侠
      - 新中式
    - 情绪模板卡:
      - 清冷月下女剑仙
      - 长安贵族千金
      - 病娇红衣妖姬
      - 白狐仙灵少女
    - 示例角色区
    - 信任补充区
  - 依赖:
    - `GET /api/styles`
    - 首页示例数据源
  - 验收:
    - 风格卡、模板卡点击后能带参数进入生成页
  - 测试: 数据渲染测试、预设带参跳转测试

### 5.2 生成工作台

- [x] `T025` 实现生成工作台主布局与 Prompt 区
  - 页面: 生成工作台
  - Figma 来源:
    - 页面 URL: `https://www.figma.com/design/0oLoQWIykGOTIvvzeMsQan/%E7%A7%91%E7%A0%94%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0?node-id=29-3195&t=yow0lQYCugEsx1ml-11`
    - 节点: `29:3195`
    - MCP 状态: 已抓取元数据
  - 关键元素:
    - 左右双栏布局
    - Prompt 输入框
    - 字数计数
    - 推荐 Prompt 标签
    - 一键灵感按钮
  - 依赖:
    - `GET /api/prompts/inspirations`
  - 验收:
    - 覆盖 `1-40 / 41-120 / 121-300 / >300` 字数提示规则
  - 测试: 输入交互测试、字数状态测试

- [x] `T026` 实现生成工作台风格选择与模板选择区
  - 页面: 生成工作台
  - Figma 来源:
    - 节点: `29:3195`
  - 关键元素:
    - 风格卡片组
    - 模板卡片组
    - 热门模板分组
  - 必须覆盖枚举:
    - 风格:
      - `style_tang_dynasty`
      - `style_han_dynasty`
      - `style_xianxia`
      - `style_new_chinese`
      - `style_gufeng_portrait`
      - `style_cinematic`
    - 模板:
      - `tpl_oc_avatar`
      - `tpl_dreamgirl_portrait`
      - `tpl_novel_heroine`
      - `tpl_hanfu_photoshoot`
      - `tpl_wallpaper_character`
      - `tpl_xiaohongshu_cover`
      - `tpl_video_cover`
      - `tpl_character_sheet`
  - 依赖:
    - `GET /api/styles`
    - `GET /api/templates`
  - 验收:
    - 切换风格时模板区联动刷新
  - 测试: 选择器联动测试、枚举完整性测试

- [x] `T027` 实现生成工作台比例选择、参考图上传与报价联动
  - 页面: 生成工作台
  - Figma 来源:
    - 节点: `29:3195`
  - 关键元素:
    - 比例选择器
    - 参考图上传器
    - 参考模式选择
    - 质量档位
    - 实时积分报价卡
  - 必须覆盖枚举:
    - 比例:
      - `ratio_square_1_1`
      - `ratio_portrait_3_4`
      - `ratio_portrait_2_3`
      - `ratio_landscape_4_3`
      - `ratio_landscape_16_9`
      - `ratio_vertical_9_16`
    - 质量:
      - `standard`
      - `hd`
      - `ultra`
    - 参考图数量:
      - `0`
      - `1`
      - `2`
      - `3`
  - 依赖:
    - 上传接口
    - `POST /api/generate/quote`
  - 验收:
    - 报价卡清晰展示基础积分、风格附加、模板附加、参考图附加、最终积分
  - 测试: 报价联动测试、上传数量上限测试

- [x] `T028` 实现生成工作台提交链路与登录拦截
  - 页面: 生成工作台
  - Figma 来源:
    - 节点: `29:3195`
  - 关键元素:
    - `立即生成` 主按钮
    - 未登录拦截弹层/跳转
    - 积分不足引导
  - 依赖:
    - `POST /api/generate/tasks`
    - 登录态
    - 充值页路由
  - 验收:
    - 未登录可先填写，提交时才要求手机号登录
    - 登录成功后恢复原参数继续提交
  - 测试: 提交流程测试、登录恢复测试、积分不足跳转测试

### 5.3 登录页 / 首登开户态

- [x] `T029` 实现手机号验证码登录页
  - 页面: 登录页
  - Figma 来源:
    - 页面 URL: `https://www.figma.com/design/0oLoQWIykGOTIvvzeMsQan/%E7%A7%91%E7%A0%94%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0?node-id=29-2472&t=yow0lQYCugEsx1ml-11`
    - 节点: `29:2472`
    - MCP 状态: 本轮未抓取
  - 页面文件来源:
    - `D:\IDEA\github\dream-draw\页面\登录页\code.html`
  - 关键元素:
    - 品牌区 Logo / 英文副标题
    - 手机号输入框
    - 验证码输入框
    - 发送验证码按钮
    - `确认进入` 主按钮
    - 新手奖励说明
    - 底部协议/支持/隐私链接
  - 依赖:
    - `POST /api/auth/sms/send-code`
    - `POST /api/auth/login`
  - 验收:
    - 只保留手机号登录
    - 不保留邮箱、密码、注册独立流程
  - 测试: 表单校验测试、验证码倒计时测试、登录成功失败测试

- [x] `T030` 实现首登开户奖励承接态
  - 页面: 首登开户态参考
  - Figma 来源:
    - 页面 URL: `https://www.figma.com/design/0oLoQWIykGOTIvvzeMsQan/%E7%A7%91%E7%A0%94%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0?node-id=29-4095&t=yow0lQYCugEsx1ml-4`
    - 节点: `29:4095`
    - MCP 状态: 已抓取元数据
  - 关键元素:
    - 首登成功提示
    - `获得 10 次免费生成机会` 奖励文案
    - 返回生成流程按钮
  - 依赖:
    - 首登标记
  - 验收:
    - 仅首登用户出现
  - 测试: 首登展示测试、老用户不展示测试

### 5.4 绘制中与生成结果

- [x] `T031` 实现绘制中状态页
  - 页面: 绘制中
  - Figma 来源:
    - 页面 URL: `https://www.figma.com/design/0oLoQWIykGOTIvvzeMsQan/%E7%A7%91%E7%A0%94%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0?node-id=29-2227&t=yow0lQYCugEsx1ml-11`
    - 节点: `29:2227`
    - MCP 状态: 本轮未抓取
  - 页面文件来源:
    - `D:\IDEA\github\dream-draw\页面\绘制中\code.html`
  - 关键元素:
    - 居中进度主视觉
    - 外环 + 墨染进度图
    - `AI 正在绘制中...` 标题
    - 预计剩余时间文案
    - 细进度条
    - Creative Tip 提示卡
    - 轮询或 SSE 状态监听
  - 依赖:
    - `GET /api/generate/tasks/{id}`
  - 验收:
    - 正确跳转 success / failed / blocked / reviewing
    - 焦点态页面不展示全局导航，保持任务沉浸式体验
  - 测试: 状态跳转测试、加载渲染测试

- [x] `T032` 实现结果页成功态、审核态、失败态、违规态
  - 页面: 生成结果
  - Figma 来源:
    - 页面 URL: `https://www.figma.com/design/0oLoQWIykGOTIvvzeMsQan/%E7%A7%91%E7%A0%94%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0?node-id=29-2078&t=yow0lQYCugEsx1ml-11`
    - 节点: `29:2078`
    - MCP 状态: 本轮未抓取
  - 页面文件来源:
    - `D:\IDEA\github\dream-draw\页面\生成结果页\code.html`
  - 关键元素:
    - 顶部导航
    - 左侧大图预览 Hero
    - 竖排风格题签
    - 右侧参数卡
    - Prompt 摘要区
    - 风格标签区
    - 下载原图按钮
    - 再次生成按钮
    - 收藏按钮
    - 分享海报预览
    - 社交渠道按钮
    - 猜你喜欢推荐区
  - 依赖:
    - `GET /api/works/{id}`
    - `POST /api/works/{id}/share`
  - 验收:
    - 参数回顾完整展示 `style_id / template_id / ratio_id / quality / reference_image_count / final_points`
  - 测试: 各状态渲染测试、参数展示测试、操作按钮测试

- [x] `T033` 实现结果页分享闭环
  - 页面: 生成结果
  - Figma 来源:
    - 节点: `29:2078`
  - 页面文件来源:
    - `D:\IDEA\github\dream-draw\页面\生成结果页\code.html`
  - 关键元素:
    - 分享图预览
    - 分享文案预览
    - 小红书 / 微信朋友圈渠道入口
    - 后续扩展 QQ / 微博渠道入口
  - 依赖:
    - `POST /api/works/{id}/share`
  - 验收:
    - 从“生成”延伸到“分享 -> 回流 -> 再生成”
  - 测试: 分享 payload 渲染测试、链接拼装测试

### 5.5 我的作品

- [x] `T034` 实现我的作品页与作品分类页签
  - 页面: 我的作品
  - Figma 来源:
    - 页面 URL: `https://www.figma.com/design/0oLoQWIykGOTIvvzeMsQan/%E7%A7%91%E7%A0%94%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0?node-id=29-2963&t=yow0lQYCugEsx1ml-11`
    - 节点: `29:2963`
    - MCP 状态: 仅 frame 元数据
  - 关键元素:
    - `我的作品`
    - `收藏作品`
    - `最近生成`
    - 作品卡片列表
  - 依赖:
    - `GET /api/works`
  - 验收:
    - 空态、加载态、错误态完整
  - 测试: tab 切换测试、列表渲染测试、空态测试

- [x] `T035` 实现作品卡片操作
  - 页面: 我的作品
  - Figma 来源:
    - 节点: `29:2963`
    - 细节按 UX 文本约束实现
  - 关键元素:
    - 查看
    - 分享
    - 再次生成
    - 收藏/取消收藏
  - 依赖:
    - 作品详情页
    - 分享接口
  - 测试: 卡片操作测试、跳转测试

### 5.6 积分充值页

- [x] `T036` 实现积分充值页
  - 页面: 积分充值
  - Figma 来源:
    - 页面 URL: `https://www.figma.com/design/0oLoQWIykGOTIvvzeMsQan/%E7%A7%91%E7%A0%94%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0?node-id=29-2263&t=yow0lQYCugEsx1ml-11`
    - 节点: `29:2263`
    - MCP 状态: 本轮未抓取
  - 页面文件来源:
    - `D:\IDEA\github\dream-draw\页面\积分充值页\code.html`
  - 关键元素:
    - 顶部导航
    - 当前积分余额
    - 左侧积分规则卡
    - 权益说明卡
    - 右侧套餐卡片区
    - 热门套餐徽标
    - 微信支付 / 支付宝单选区
    - `立即充值` 主按钮
    - 充值协议提示
  - 必须覆盖套餐:
    - `30积分 / 9.9`
    - `100积分 / 29.9`
    - `300积分 / 69.9`
  - 依赖:
    - `POST /api/pay/orders`
  - 验收:
    - 支持微信支付和支付宝
    - 虽然本地 HTML 原型展示的是旧套餐数值，实际实现必须以 PRD 枚举为准
  - 测试: 套餐选择测试、下单测试、支付态测试

---

## 6. 管理端页面任务

### 6.1 管理员登录页

- [x] `T037` 实现管理员登录页
  - 页面: 管理员登录页
  - Figma 来源:
    - 复用登录页视觉参考: `29:2472`
    - MCP 状态: 本轮未抓取
  - 关键元素:
    - 账号输入框
    - 密码输入框
    - 登录按钮
    - 错误提示区
  - 依赖:
    - `POST /api/admin/login`
  - 测试: 登录表单测试、错误提示测试

### 6.2 用户管理页

- [x] `T038` 实现用户管理页
  - 页面: 用户管理
  - Figma 来源:
    - 页面 URL: `https://www.figma.com/design/0oLoQWIykGOTIvvzeMsQan/%E7%A7%91%E7%A0%94%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0?node-id=29-2534&t=yow0lQYCugEsx1ml-11`
    - 节点: `29:2534`
    - MCP 状态: 本轮未抓取
  - 页面文件来源:
    - `D:\IDEA\github\dream-draw\页面\用户管理\code.html`
  - 关键元素:
    - 左侧后台侧边导航
    - 页面标题区
    - 导出数据按钮
    - 创建用户按钮
    - 搜索框
    - 状态筛选
    - 注册时间排序筛选
    - 用户表格
    - 行内详情按钮
    - 行内冻结/解冻按钮
    - 分页器
  - 表格字段:
    - 用户 ID
    - 用户信息
    - 剩余积分
    - 账号状态
    - 最后登录时间
    - 账号状态
  - 依赖:
    - `GET /api/admin/users`
  - 测试: 搜索筛选测试、表格渲染测试、状态操作测试

### 6.3 用户详情页

- [x] `T039` 实现用户详情页
  - 页面: 用户详情
  - Figma 来源:
    - 页面 URL: `https://www.figma.com/design/0oLoQWIykGOTIvvzeMsQan/%E7%A7%91%E7%A0%94%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0?node-id=29-2748&t=yow0lQYCugEsx1ml-11`
    - 节点: `29:2748`
    - MCP 状态: 因限流抓取失败
  - 页面文件来源:
    - `D:\IDEA\github\dream-draw\页面\用户详情页\code.html`
  - 关键元素:
    - 面包屑导航
    - UID 标识
    - 审计日志按钮
    - 冻结账号按钮
    - 调整积分按钮
    - 用户基础信息卡
    - 账户等级与实名认证状态
    - 积分余额卡
    - 积分流水表
    - 创作记录宫格
    - 创作统计摘要
  - 依赖:
    - `GET /api/admin/users/{id}`
    - `PATCH /api/admin/users/{id}/points`
    - `PATCH /api/admin/users/{id}/status`
  - 验收:
    - 危险操作必须二次确认并填写原因
  - 测试: 详情页渲染测试、危险操作测试

### 6.4 模型配置中心

- [x] `T040` 实现模型配置中心页面
  - 页面: 模型配置中心
  - Figma 来源:
    - 页面 URL: `https://www.figma.com/design/0oLoQWIykGOTIvvzeMsQan/%E7%A7%91%E7%A0%94%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0?node-id=29-3434&t=yow0lQYCugEsx1ml-11`
    - 节点: `29:3434`
    - MCP 状态: 已抓取元数据
  - 关键元素:
    - Provider 列表区
    - 筛选区
    - 新增/编辑配置表单
    - 默认/备用模型设置区
  - 表单字段:
    - `provider_id`
    - `provider_name`
    - `base_url`
    - `api_key_ref`
    - `model_name`
    - `api_mode`
    - `capabilities`
    - `priority`
    - `status`
    - `timeout_seconds`
    - `qps_limit`
    - `cost_level`
  - 依赖:
    - `GET/POST /api/admin/model-providers`
    - `PATCH /api/admin/model-providers/{id}`
    - `PATCH /api/admin/model-providers/{id}/status`
  - 验收:
    - `api_mode` 固定展示为 `openai_compatible`
  - 测试: 表单校验测试、增改状态切换测试

### 6.5 模型状态监控页

- [x] `T041` 实现模型状态监控页
  - 页面: 模型状态监控
  - Figma 来源:
    - 页面 URL: `https://www.figma.com/design/0oLoQWIykGOTIvvzeMsQan/%E7%A7%91%E7%A0%94%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0?node-id=29-3651&t=yow0lQYCugEsx1ml-11`
    - 节点: `29:3651`
    - MCP 状态: 已抓取元数据
  - 关键元素:
    - 状态总览卡
    - 模型监控表
    - 成功率指标区
    - 响应时间指标区
    - 告警列表
    - 一键切换模型入口
  - 必须覆盖状态枚举:
    - `healthy`
    - `degraded`
    - `unavailable`
    - `maintenance`
  - 依赖:
    - `GET /api/admin/model-monitoring`
  - 验收:
    - 状态颜色与文案映射严格一致
  - 测试: 指标渲染测试、状态渲染测试、空态测试

---

## 7. 集成、质量与发布前验证

- [x] `T042` 打通用户完整主链路集成测试
  - 场景:
    - 游客浏览首页
    - 进入生成页
    - 手机号登录
    - 提交生成
    - 查看结果
    - 下载图片
  - 目标:
    - 覆盖“用户能完成一次登录-生成-查看-下载的完整流程”
  - 测试: 端到端测试

- [x] `T043` 打通分享回流闭环测试
  - 场景:
    - 结果页分享
    - 新用户回流
    - 新用户登录并完成首次生成
  - 测试: 端到端测试

- [x] `T044` 打通后台管理链路测试
  - 场景:
    - 管理员登录
    - 查看用户
    - 查看用户详情
    - 维护积分或状态
    - 查看模型配置
    - 查看模型监控
  - 测试: 后台端到端测试

- [x] `T045` 完成性能、风控与失败兜底验证
  - 范围:
    - 游客禁止生成
    - 新用户每日次数限制
    - IP 限流
    - Prompt 重复防刷
    - 生成失败退款
    - 模型异常降级
  - 测试: 集成测试、限流测试、异常测试

- [x] `T046` 完成文档同步与 closeout 准备
  - 范围:
    - 回写任务状态
    - 更新必要 README / 设计文档
    - 准备 `/adpp:closeout`
  - 测试: 文档完整性检查

---

## 8. 推荐实施顺序

1. `T001-T004` 基础工程与共享枚举
2. `T005-T015` 用户侧后端主链路
3. `T016-T019` 管理端后端能力
4. `T020-T022` 前端公共层
5. `T023-T036` 用户端页面
6. `T037-T041` 管理端页面
7. `T042-T046` 集成验证与收口

---

## 9. 可并行任务组

- 任务组 A:
  - `T005` 数据库迁移
  - `T002` 前端骨架
  - `T003` 枚举中心

- 任务组 B:
  - `T006` 登录
  - `T008` 风格/模板/灵感接口
  - `T018` 模型配置接口

- 任务组 C:
  - `T023-T024` 首页
  - `T029-T030` 登录页与首登态
  - `T037` 管理员登录页

- 任务组 D:
  - `T040` 模型配置中心
  - `T041` 模型状态监控页

---

## 10. Figma 映射备注

- 已有 MCP 元数据页面:
  - 首页 `29:3917`
  - 生成工作台 `29:3195`
  - 首登开户态参考 `29:4095`
  - 我的作品 `29:2963`
  - 模型配置中心 `29:3434`
  - 模型状态监控 `29:3651`

- 因限流未完整抓取或失败页面:
  - 登录页 `29:2472`
  - 用户管理 `29:2534`
  - 用户详情 `29:2748`
  - 积分充值 `29:2263`
  - 绘制中 `29:2227`
  - 生成结果 `29:2078`

- 上述未完整抓取页面，本轮以前端 UX 文本约束和页面 URL 为主，后续若 Figma MCP 限流恢复，可补充更细的节点级实现任务。
