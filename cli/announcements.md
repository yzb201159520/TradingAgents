# cli/announcements.py 逻辑说明

## 文件用途
从远程 API 获取项目公告并在 CLI 中显示，支持"需要关注"公告的强制确认交互。

## 核心逻辑

### 公告获取
1. 从 `CLI_CONFIG` 读取公告端点 URL、超时时间和回退文本。
2. 使用 `requests.get()` 调用远程 API（默认 `https://api.tauric.ai/v1/announcements`，超时 1 秒）。
3. 解析 JSON 响应，提取 `announcements`（公告文本列表）和 `require_attention`（是否需要用户确认）。
4. 任何异常（网络错误、超时、解析失败）均静默处理，返回回退文本（指向 GitHub 仓库的链接）。

### 公告显示
1. 使用 Rich `Panel` 渲染公告内容，标题为 "Announcements"，边框样式为 cyan。
2. 如果 `require_attention` 为 True，使用 `getpass.getpass()` 暂停等待用户按 Enter 确认（`getpass` 不回显输入，适合无需输入内容的确认场景）。
3. 如果 `require_attention` 为 False，仅打印空行继续。

## 关键函数/类

- **`fetch_announcements(url, timeout)`**：获取远程公告
  - `url`：公告端点 URL，默认取 `CLI_CONFIG["announcements_url"]`
  - `timeout`：请求超时秒数，默认取 `CLI_CONFIG["announcements_timeout"]`
  - 返回 `dict`，包含 `announcements`（列表）和 `require_attention`（布尔值）
- **`display_announcements(console, data)`**：在 Rich Console 中显示公告
  - `console`：Rich Console 实例
  - `data`：`fetch_announcements` 返回的字典

## 与其他模块的关系
- **依赖**：
  - `cli.config.CLI_CONFIG`：CLI 配置字典（公告 URL、超时、回退文本）
  - `requests`：HTTP 请求库
  - `rich.console.Console` / `rich.panel.Panel`：Rich TUI 组件
  - `getpass`：标准库，用于等待用户按 Enter
- **被依赖**：
  - `cli/main.py`：在分析引导开始前调用 `fetch_announcements()` 和 `display_announcements()` 展示公告
