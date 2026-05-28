# reddit.py 逻辑说明

## 文件用途
从 Reddit 公开 JSON 端点获取与指定股票相关的讨论帖，返回格式化的纯文本块供 LLM 提示词注入，用于社交媒体情绪分析。

## 核心逻辑
1. **无 API Key 设计**：使用 Reddit 的公开 JSON 接口（`/r/{sub}/search.json`），无需 API 密钥，但受限于约每分钟 10 次请求的速率限制。

2. **子版块遍历**：默认在 `wallstreetbets`、`stocks`、`investing` 三个财经子版块中搜索。搜索参数包括：
   - 搜索关键词为股票代码
   - `restrict_sr=on` 限定在当前子版块内搜索
   - `sort=new` 按最新排序
   - `t=week` 限定过去 7 天
   - `limit` 控制每个子版块返回的帖子数

3. **请求节流**：通过 `inter_request_delay`（默认 0.4 秒）在子版块请求之间插入延迟，确保不触发 Reddit 的公共速率限制。

4. **格式化输出**：对每个帖子提取标题、得分（↑）、评论数（c）、发布日期、正文摘要（超过 240 字符截断）。按子版块分组，汇总为纯文本块。

5. **优雅降级**：任何网络错误、JSON 解析失败均被捕获并记录警告，返回占位符文本而非抛出异常，确保调用方无需特殊处理缺失数据的情况。

## 关键函数/类
- **`_fetch_subreddit(ticker, sub, limit, timeout) -> list[dict]`**
  - 内部函数，对单个子版块发起搜索请求
  - `ticker`：股票代码
  - `sub`：子版块名称
  - `limit`：返回帖子数上限
  - `timeout`：请求超时秒数
  - 返回帖子数据字典列表，失败时返回空列表

- **`fetch_reddit_posts(ticker, subreddits, limit_per_sub, timeout, inter_request_delay) -> str`**
  - `ticker`：股票代码
  - `subreddits`：要搜索的子版块可迭代对象，默认 `("wallstreetbets", "stocks", "investing")`
  - `limit_per_sub`：每个子版块最多返回帖子数，默认 5
  - `timeout`：单次请求超时，默认 10.0 秒
  - `inter_request_delay`：请求间延迟，默认 0.4 秒
  - 返回格式化的纯文本字符串，无帖子时返回占位符

- **`DEFAULT_SUBREDDITS`**：默认子版块元组，按信号密度排序（wallstreetbets 流量最大但噪音也最多，stocks/investing 更理性）

## 与其他模块的关系
- **依赖**：仅使用 Python 标准库（`json`、`urllib`、`time`、`logging`），无项目内部依赖
- **被依赖**：`agents/analysts/sentiment_analyst.py` — 情绪分析师直接调用 `fetch_reddit_posts` 获取 Reddit 讨论数据
