# fundamentals_analyst.py 逻辑说明

## 文件用途
基本面分析师 Agent，负责通过财务数据工具获取公司基本面信息（财务报表、公司概况等），生成基本面分析报告。

## 核心逻辑
1. 采用闭包工厂模式：`create_fundamentals_analyst(llm)` 返回 `fundamentals_analyst_node(state)` 内部函数。
2. 从 `state` 中提取当前交易日 (`trade_date`) 和标的名称 (`company_of_interest`)，构建工具上下文。
3. 注册四个工具：
   - `get_fundamentals`：综合公司分析。
   - `get_balance_sheet`：资产负债表。
   - `get_cashflow`：现金流量表。
   - `get_income_statement`：利润表。
4. 系统提示词要求 LLM 撰写涵盖财务文件、公司概况、基本财务数据和财务历史的综合报告，提供可操作的洞察和支撑证据，并在报告末尾附加 Markdown 汇总表格。
5. 使用 `ChatPromptTemplate` 组装提示词，包含系统消息和 `MessagesPlaceholder`。
6. 通过 `llm.bind_tools(tools)` 构建带工具调用能力的 LLM 链，执行调用。
7. 如果 LLM 未发起工具调用，则将 `result.content` 作为报告；否则报告为空字符串。
8. 返回更新后的 `messages` 和 `fundamentals_report`。

## 关键函数/类
- **`create_fundamentals_analyst(llm)`**：工厂函数，接收 LLM 实例，返回 `fundamentals_analyst_node` 节点函数。
- **`fundamentals_analyst_node(state)`**：LangGraph 节点函数，执行基本面分析流程。
  - `state`：需包含 `trade_date`、`company_of_interest`、`messages`。

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.utils.agent_utils`：`build_instrument_context`、`get_fundamentals`、`get_balance_sheet`、`get_cashflow`、`get_income_statement`、`get_language_instruction`。
  - `tradingagents.dataflows.config`：`get_config`。
  - `langchain_core.prompts`：提示词模板构建。
- **被依赖**：
  - 输出 `fundamentals_report` 被 Bull/Bear Researcher、三个 Risk Debator 和 Portfolio Manager 消费。
  - 输出 `messages` 被 LangGraph 图消息路由机制使用。
