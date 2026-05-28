# cli/config.py 逻辑说明

## 文件用途
CLI 模块的静态配置字典，集中管理公告功能的端点 URL、超时时间和回退文本等常量。

## 核心逻辑
定义 `CLI_CONFIG` 字典，包含三个键值对：
- `announcements_url`：公告 API 端点地址（`https://api.tauric.ai/v1/announcements`）
- `announcements_timeout`：请求超时秒数（1.0 秒，确保 CLI 响应性）
- `announcements_fallback`：获取公告失败时的回退文本，包含指向 GitHub 仓库的 Rich 标记链接

配置值被 `cli/announcements.py` 读取使用，集中管理便于统一修改。

## 关键函数/类
无（仅包含 `CLI_CONFIG` 字典常量）。

## 与其他模块的关系
- **依赖**：无
- **被依赖**：
  - `cli/announcements.py`：读取 `CLI_CONFIG` 获取公告端点、超时和回退文本
