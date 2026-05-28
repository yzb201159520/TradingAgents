# agent_states.py 逻辑说明

## 文件用途
定义 TradingAgents 多智能体图的状态数据结构，为 LangGraph StateGraph 提供节点间信息传递的类型化载体。

## 核心逻辑

本文件使用 `TypedDict` 定义了三个状态类，分别对应系统中三个核心阶段的数据流：

1. **研究辩论阶段**（`InvestDebateState`）：多头（Bull）与空头（Bear）研究员之间围绕"是否投资"展开辩论，记录双方发言历史、当前回复、裁判判决及对话轮次。

2. **风险辩论阶段**（`RiskDebateState`）：激进（Aggressive）、保守（Conservative）、中立（Neutral）三个风险分析师围绕"风险如何评估"展开辩论，记录三方发言历史与当前回复、最新发言者、裁判判决及对话轮次。

3. **全局智能体状态**（`AgentState`）：继承 LangGraph 的 `MessagesState`（自带 `messages` 字段用于工具调用消息传递），承载贯穿整个流水线的全局信息，包括：
   - 交易标的元信息（公司、资产类型、交易日期）
   - 各分析师产出的报告（市场、情绪、新闻、基本面）
   - 研究辩论子状态与投资计划
   - 交易员投资计划
   - 风险辩论子状态与最终交易决策
   - 历史记忆上下文（同标的过往决策 + 跨标的经验教训）

所有字段均使用 `Annotated[type, description]` 标注，提供自文档化的类型与语义信息，便于 LLM 在工具调用时理解字段含义。

## 关键函数/类

### `InvestDebateState(TypedDict)`
研究辩论阶段的状态结构。
- `bull_history`：多方发言历史
- `bear_history`：空方发言历史
- `history`：完整对话历史
- `current_response`：最新回复
- `judge_decision`：裁判判决
- `count`：当前对话轮次

### `RiskDebateState(TypedDict)`
风险辩论阶段的状态结构。
- `aggressive_history` / `conservative_history` / `neutral_history`：三方发言历史
- `history`：完整对话历史
- `latest_speaker`：最近发言者标识
- `current_aggressive_response` / `current_conservative_response` / `current_neutral_response`：三方当前回复
- `judge_decision`：裁判判决
- `count`：当前对话轮次

### `AgentState(MessagesState)`
全局智能体状态，贯穿整个 LangGraph 图。
- 继承 `MessagesState` 获得 `messages` 字段
- 包含标的信息、四份分析师报告、两类辩论子状态、投资计划、最终决策及历史记忆上下文

## 与其他模块的关系
- **依赖**：`typing`（标准库）、`typing_extensions`（`TypedDict`）、`langgraph.graph.MessagesState`（LangGraph 内置消息状态）
- **被依赖**：
  - `tradingagents.graph.trading_graph`：主图构建，导入全部三个状态类
  - `tradingagents.graph.propagation.py`：状态初始化与传播，导入全部三个状态类
  - `tradingagents.graph.conditional_logic.py`：条件路由逻辑，导入 `AgentState`
  - `tradingagents.graph.setup.py`：图节点注册，导入 `AgentState`
