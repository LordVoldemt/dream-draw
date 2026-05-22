# Debug Session: image-not-visible

- Status: [OPEN]
- Started: 2026-05-22
- Symptom: 前端请求 `http://127.0.0.1:5174/uploads/works/task-19.png` 返回 304，但页面看不到图片。
- Expected: 生成结果页或列表页可以正常显示 `/uploads/works/task-19.png`。

## Hypotheses

1. Vite 开发服务器对 `/uploads` 的代理或静态映射不正确，304 来自前端开发服务器而不是后端静态文件服务。
2. 文件本身存在，但返回的缓存协商结果导致浏览器命中旧响应，而旧响应实际为空或损坏。
3. 数据库存储的 `image_url` 正确，但页面实际渲染节点使用了错误字段、错误路径或样式把图片隐藏了。
4. 后端确实生成了文件，但文件内容不是合法图片，浏览器虽然请求成功却无法渲染。
5. 结果页/生成中页在任务完成后没有正确刷新到最新 work 数据，仍引用旧 task 的资源地址。

## Evidence Plan

- 检查前端 dev server 对 `/uploads` 的处理方式。
- 检查后端 `StaticFiles` 映射与 uploads 目录实际文件。
- 对图片生成完成、作品读取、前端结果页取图链路增加最小日志插桩。
- 必要时直接请求文件并检查响应头、响应体大小。

## Current Step

- 初始化调试记录，准备先做静态链路检查与最小插桩。
