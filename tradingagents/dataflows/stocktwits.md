# stocktwits.py 逻辑说明

## 文件用途
从 StockTwits 公开 API 获取指定股票的最新消息流，提取用户标注的情绪标签（看多/看空），返回格式化的纯文本块供 LLM 提示词注入，用于社交媒体情绪分析。

## 核心逻辑
1. **无 API Key 设计**：使用 StockTwits 的公开符号流端点（`/api/2/streams/symbol/{ticker}.json`），无需 API 密钥、OAuth 或注册。

2. **消息获取与解析**：
   - 构造请求 URL（ticker 转大写），设置 User-Agent 和 Accept 头。
   - 解析返回 JSON 中的 `messages` 数组，每条消息包含 `body`（正文）、`created_at`（时间戳）、`user.username`（用户名）和 `entities.sentiment.basic`（情绪标签）。

3. **情绪统计**：
   - 遍历消息，统计 Bullish（看多）、Bearish（看空）、无标签三类数量。
   - 计算看多/看空百分比。
   - 输出包含统计摘要和逐条消息的格式化文本。

4. **文本截断**：消息正文超过 280 字符时截断并添加省略号。

5. **优雅降级**：任何 HTTP 错误、URL 错误、JSON 解析失败、超时均被捕获并记录警告，返回占位符字符串（如 `<stocktwits unavailable: HTTPError>` 或 `<no StockTwits messages found for $AAPL>`），确保调用方不会因网络问题而中断。

## 关键函数/类
- **`fetch_stocktwits_messages(ticker, limit, timeout) -> str`**
  - `ticker`：股票代码
  - `limit`：返回消息数上限，默认 30
  - `timeout`：请求超时秒数，默认 10.0
  - 返回格式化的纯文本字符串，包含情绪统计摘要和逐条消息列表；失败时返回占位符

## 与其他模块的关系
- **依赖**：仅使用 Python 标准库（`json`、`urllib`、`datetime`、`logging`），无项目内部依赖
- **被依赖**：`agents/analysts/sentiment_analyst.py` — 情绪分析师直接调用 `fetch_stocktwits_messages` 获取 StockTwits 消息流数据
