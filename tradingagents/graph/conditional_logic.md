# conditional_logic.py 逻辑说明

## 文件用途
定义 StateGraph 中所有条件边的路由逻辑，控制分析师工具调用循环、投资辩论循环和风险辩论循环的流转与终止。

## 核心逻辑

### 分析师工具调用路由
每位分析师（Market / Social / News / Fundamentals）都有对应的 `should_continue_*` 方法，逻辑一致：
1. 检查状态中最后一条消息是否包含 `tool_calls`。
2. 若有工具调用 → 路由到对应的 `tools_*` 节点执行工具。
3. 若无工具调用 → 路由到 `Msg Clear *` 节点清除消息，准备进入下一阶段。

### 投资辩论循环 (`should_continue_debate`)
控制 Bull Researcher 与 Bear Researcher 之间的多轮辩论：
1. 当 `investment_debate_state["count"]` 达到 `2 * max_debate_rounds` 时，辩论结束，路由到 Research Manager。
2. 若当前发言者以 "Bull" 开头 → 路由到 Bear Researcher（轮换发言）。
3. 否则 → 路由到 Bull Researcher。

计数说明：每对一次 Bull→Bear 交锋计为 2 次 count，因此 `2 * max_debate_rounds` 表示 max_debate_rounds 轮完整交锋。

### 风险辩论循环 (`should_continue_risk_analysis`)
控制 Aggressive / Conservative / Neutral 三位分析师之间的循环辩论：
1. 当 `risk_debate_state["count"]` 达到 `3 * max_risk_discuss_rounds` 时，辩论结束，路由到 Portfolio Manager。
2. 根据 `latest_speaker` 字段判断上一位发言者，按固定顺序轮换：
   - Aggressive → Conservative → Neutral → Aggressive → ...
3. 计数说明：三位分析师各发言一次为一个完整循环（count 增加 3），`3 * max_risk_discuss_rounds` 表示 max_risk_discuss_rounds 轮完整循环。

### 命名兼容性说明
`should_continue_social` 方法名保留 "social" 后缀是为了与 `AnalystType.SOCIAL = "social"` 的配置向后兼容，但返回的清除节点标签为 `Msg Clear Sentiment`，匹配 v0.2.5 的重命名。

## 关键函数/类

### `ConditionalLogic`
- **参数**：`max_debate_rounds`（投资辩论轮数，默认 1）、`max_risk_discuss_rounds`（风险辩论轮数，默认 1）
- **方法**：
  - `should_continue_market(state)` — 市场分析师工具路由
  - `should_continue_social(state)` — 情绪分析师工具路由
  - `should_continue_news(state)` — 新闻分析师工具路由
  - `should_continue_fundamentals(state)` — 基本面分析师工具路由
  - `should_continue_debate(state) -> str` — 投资辩论循环路由
  - `should_continue_risk_analysis(state) -> str` — 风险辩论循环路由

## 与其他模块的关系
- **依赖**：`tradingagents.agents.utils.agent_states.AgentState`（读取状态字段）
- **被依赖**：`setup.py`（GraphSetup 在构建图时将条件方法注册为条件边）、`trading_graph.py`（创建 ConditionalLogic 实例并注入 GraphSetup）
