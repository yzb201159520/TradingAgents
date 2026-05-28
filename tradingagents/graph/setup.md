# setup.py 逻辑说明

## 文件用途
构建 LangGraph StateGraph 工作流，定义所有节点及其连接关系，实现五阶段多智能体交易分析流水线。

## 核心逻辑

### 五阶段流水线架构
Graph 通过以下阶段组织节点：

1. **分析师阶段**：Market → Sentiment → News → Fundamentals（按 `selected_analysts` 列表顺序串联）
   - 每位分析师后接条件边：若分析师发起工具调用 → 执行 ToolNode → 返回分析师节点；否则 → Msg Clear 节点清除消息 → 进入下一位分析师。
   - 最后一位分析师的 Msg Clear 节点连接到 Bull Researcher。

2. **研究辩论阶段**：Bull Researcher ⇄ Bear Researcher（条件循环）
   - 辩论轮次由 `should_continue_debate` 控制。
   - 辩论结束 → Research Manager 综合双方观点生成投资计划。

3. **交易员阶段**：Research Manager → Trader
   - Trader 根据投资计划制定交易方案。

4. **风险辩论阶段**：Aggressive Analyst → Conservative Analyst → Neutral Analyst（条件循环）
   - 辩论轮次由 `should_continue_risk_analysis` 控制。
   - 三位分析师按固定顺序轮换发言。
   - 辩论结束 → Portfolio Manager。

5. **投资组合经理阶段**：Portfolio Manager → END
   - 做出最终交易决策，图执行结束。

### 动态分析师选择
通过 `selected_analysts` 参数（默认 `["market", "social", "news", "fundamentals"]`），调用 `build_analyst_execution_plan` 生成执行计划，动态决定图中的分析师节点。这使图结构可以根据需求灵活裁剪。

### 分析师节点三元组
每位分析师在图中注册三个节点：
- `agent_node`（如 "Market Analyst"）— 分析师智能体
- `tool_node`（如 "tools_market"）— 工具执行节点
- `clear_node`（如 "Msg Clear Market"）— 消息清除节点

### 消息清除机制
每位分析师完成工具调用后，Msg Clear 节点（`create_msg_delete()`）清除累积的消息历史，避免上下文窗口溢出并防止分析师之间的消息串扰。

## 关键函数/类

### `GraphSetup`
- **参数**：
  - `quick_thinking_llm` — 快速推理 LLM（用于分析师、研究员、交易员等）
  - `deep_thinking_llm` — 深度推理 LLM（用于 Research Manager、Portfolio Manager）
  - `tool_nodes` — 各分析师对应的工具节点字典 `{"market": ToolNode, ...}`
  - `conditional_logic` — ConditionalLogic 实例，提供条件边判断方法
  - `analyst_concurrency_limit` — 分析师并发限制（默认 1）

- **方法**：
  - `setup_graph(selected_analysts)` — 构建并返回 StateGraph 工作流对象。参数为选中的分析师类型列表。

## 与其他模块的关系
- **依赖**：
  - `langgraph.graph`（StateGraph, START, END）
  - `langgraph.prebuilt.ToolNode`
  - `tradingagents.agents`（所有智能体工厂函数：`create_market_analyst`、`create_sentiment_analyst` 等）
  - `tradingagents.agents.utils.agent_states.AgentState`
  - `.analyst_execution.build_analyst_execution_plan`（生成执行计划）
  - `.conditional_logic.ConditionalLogic`（条件边逻辑）
- **被依赖**：`trading_graph.py`（TradingAgentsGraph 初始化时调用 GraphSetup.setup_graph() 获取工作流）
