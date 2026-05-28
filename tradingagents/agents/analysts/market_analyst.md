# market_analyst.py 逻辑说明

## 文件用途
市场技术分析师 Agent，负责通过技术指标工具获取行情数据并生成技术分析报告，为后续研究辩论提供量化趋势依据。

## 核心逻辑
1. 采用闭包工厂模式：`create_market_analyst(llm)` 返回 `market_analyst_node(state)` 内部函数。
2. 从 `state` 中提取当前交易日 (`trade_date`)、资产类型 (`asset_type`) 和标的名称 (`company_of_interest`)，构建工具上下文。
3. 注册两个工具：`get_stock_data`（获取历史行情 CSV）和 `get_indicators`（计算技术指标）。
4. 系统提示词要求 LLM 先调用 `get_stock_data` 获取基础行情数据，再调用 `get_indicators` 选择最多 8 个互补指标（涵盖均线、MACD、动量、波动率、成交量等类别），避免冗余。
5. 使用 `ChatPromptTemplate` 组装提示词，包含系统消息（角色定义 + 指标选择指南 + 语言指令）和 `MessagesPlaceholder`（对话消息）。
6. 通过 `llm.bind_tools(tools)` 构建带工具调用能力的 LLM 链，执行调用。
7. 如果 LLM 未发起工具调用（`result.tool_calls` 为空），则将 `result.content` 作为报告；否则报告为空字符串（由后续 ToolNode 处理）。
8. 返回更新后的 `messages` 和 `market_report`。

## 关键函数/类
- **`create_market_analyst(llm)`**：工厂函数，接收 LLM 实例，返回 `market_analyst_node` 节点函数。
  - `llm`：LangChain 兼容的 LLM 实例，需支持 `bind_tools()`。
- **`market_analyst_node(state)`**：LangGraph 节点函数，执行技术分析流程。
  - `state`：图状态字典，需包含 `trade_date`、`company_of_interest`、`messages`，可选 `asset_type`。

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.utils.agent_utils`：提供 `get_stock_data`、`get_indicators`、`build_instrument_context`、`get_language_instruction` 工具函数。
  - `tradingagents.dataflows.config`：提供 `get_config`（获取运行配置）。
  - `langchain_core.prompts`：提示词模板构建。
- **被依赖**：
  - 输出 `market_report` 被 Bull/Bear Researcher、三个 Risk Debator 和 Portfolio Manager 消费。
  - 输出 `messages` 被 LangGraph 图的消息路由机制使用。
