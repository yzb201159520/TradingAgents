# news_analyst.py 逻辑说明

## 文件用途
新闻分析师 Agent，负责通过新闻检索工具获取公司相关新闻和全球宏观经济新闻，生成新闻分析报告。

## 核心逻辑
1. 采用闭包工厂模式：`create_news_analyst(llm)` 返回 `news_analyst_node(state)` 内部函数。
2. 从 `state` 中提取当前交易日 (`trade_date`)、资产类型 (`asset_type`) 和标的名称 (`company_of_interest`)，构建工具上下文。
3. 注册两个工具：
   - `get_news(query, start_date, end_date)`：获取公司特定或针对性新闻搜索。
   - `get_global_news(curr_date, look_back_days, limit)`：获取更广泛的宏观经济新闻。
4. 系统提示词要求 LLM 撰写与交易和宏观经济相关的综合新闻报告，根据资产类型动态调整术语（stock → "company"，crypto → "asset"）。
5. 使用 `ChatPromptTemplate` 组装提示词，包含系统消息和 `MessagesPlaceholder`。
6. 通过 `llm.bind_tools(tools)` 构建带工具调用能力的 LLM 链，执行调用。
7. 如果 LLM 未发起工具调用，则将 `result.content` 作为报告；否则报告为空字符串（由后续 ToolNode 处理）。
8. 返回更新后的 `messages` 和 `news_report`。

## 关键函数/类
- **`create_news_analyst(llm)`**：工厂函数，接收 LLM 实例，返回 `news_analyst_node` 节点函数。
- **`news_analyst_node(state)`**：LangGraph 节点函数，执行新闻分析流程。
  - `state`：需包含 `trade_date`、`company_of_interest`、`messages`，可选 `asset_type`。

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.utils.agent_utils`：`build_instrument_context`、`get_news`、`get_global_news`、`get_language_instruction`。
  - `tradingagents.dataflows.config`：`get_config`。
  - `langchain_core.prompts`：提示词模板构建。
- **被依赖**：
  - 输出 `news_report` 被 Bull/Bear Researcher、三个 Risk Debator 和 Portfolio Manager 消费。
  - 输出 `messages` 被 LangGraph 图消息路由机制使用。
