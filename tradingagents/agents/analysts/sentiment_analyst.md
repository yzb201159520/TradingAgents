# sentiment_analyst.py 逻辑说明

## 文件用途
多源情绪分析师 Agent，负责聚合 Yahoo Finance 新闻、StockTwits 散户帖子、Reddit 社区帖子三类数据，生成综合情绪分析报告。

## 核心逻辑
1. 采用闭包工厂模式：`create_sentiment_analyst(llm)` 返回 `sentiment_analyst_node(state)` 内部函数。
2. **与工具调用型分析师不同，本 Agent 不使用 `bind_tools()`**，而是在节点执行时预取三路数据并注入提示词：
   - `get_news.func(ticker, start_date, end_date)`：获取过去 7 天的 Yahoo Finance 新闻标题。
   - `fetch_stocktwits_messages(ticker, limit=30)`：获取 StockTwits 按 cashtag 索引的散户帖子，含用户标注的 Bullish/Bearish 情绪标签。
   - `fetch_reddit_posts(ticker)`：获取 r/wallstreetbets、r/stocks、r/investing 子版块帖子。
3. 每个数据源以容错方式获取，返回字符串（真实数据或占位符），保证 LLM 始终能收到有效输入。
4. `_build_system_message()` 将三路数据以结构化 XML 标签（`<start_of_news>`/`<end_of_news>` 等）嵌入系统提示词，并给出最佳分析实践：
   - 将 StockTwits Bullish/Bearish 比率作为领先散户情绪信号。
   - 识别跨源分歧（如新闻看空但散户看多）。
   - 按 Reddit 参与度加权（upvote/comment 数量）。
   - 区分事实事件与主观观点。
   - 识别反复出现的叙事主题。
   - 诚实标记数据限制。
5. 使用 `prompt | llm`（不含 `bind_tools`）单次调用生成报告。
6. 输出报告要求包含：整体情绪方向、逐源拆解、分歧与对齐、催化剂与风险、Markdown 汇总表格。
7. 提供 `create_social_media_analyst(llm)` 作为向后兼容别名（已弃用），内部调用 `create_sentiment_analyst` 并发出 `DeprecationWarning`。

## 关键函数/类
- **`create_sentiment_analyst(llm)`**：工厂函数，返回 `sentiment_analyst_node` 节点。
- **`sentiment_analyst_node(state)`**：LangGraph 节点函数，预取数据并生成情绪报告。
  - `state`：需包含 `company_of_interest`、`trade_date`、`messages`。
- **`_build_system_message(...)`**：组装含三路预取数据的系统提示词。
  - 参数：`ticker`、`start_date`、`end_date`、`news_block`、`stocktwits_block`、`reddit_block`。
- **`create_social_media_analyst(llm)`**：已弃用的兼容别名，内部调用 `create_sentiment_analyst`。
- **`_seven_days_back(trade_date)`**：将交易日期回退 7 天，返回起止日期。

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.utils.agent_utils`：`build_instrument_context`、`get_language_instruction`、`get_news`。
  - `tradingagents.dataflows.reddit`：`fetch_reddit_posts`。
  - `tradingagents.dataflows.stocktwits`：`fetch_stocktwits_messages`。
  - `langchain_core.prompts`：提示词模板构建。
- **被依赖**：
  - 输出 `sentiment_report` 被 Bull/Bear Researcher、三个 Risk Debator 和 Portfolio Manager 消费。
  - 输出 `messages` 被 LangGraph 图消息路由机制使用。
  - `social_media_analyst.py` 作为向后兼容桥接，从此文件导入 `create_sentiment_analyst` 和 `create_social_media_analyst`。
