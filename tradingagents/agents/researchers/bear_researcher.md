# bear_researcher.py 逻辑说明

## 文件用途
看空研究员 Agent，在研究辩论阶段负责基于分析师报告构建看空论据，与看多研究员进行交替辩论。

## 核心逻辑
1. 采用闭包工厂模式：`create_bear_researcher(llm)` 返回 `bear_node(state)` 内部函数。
2. 从 `state` 中提取辩论状态 (`investment_debate_state`) 和四份分析师报告（`market_report`、`sentiment_report`、`news_report`、`fundamentals_report`）。
3. 根据资产类型 (`asset_type`) 动态调整提示词标签（与 Bull Researcher 一致）。
4. 提示词要求 LLM 扮演看空分析师，聚焦以下方面：
   - 风险与挑战：市场饱和、财务不稳定、宏观经济威胁。
   - 竞争弱点：市场定位弱势、创新衰退、竞争威胁。
   - 负面指标：财务数据、市场趋势、不利新闻。
   - 反驳看多论点：揭露看多方的过度乐观假设。
   - 互动式辩论风格：直接回应看多方观点。
5. 使用 `llm.invoke(prompt)` 单次调用生成论据，将响应格式化为 `"Bear Analyst: {response.content}"`。
6. 更新 `investment_debate_state`：
   - `history`：追加当前看空论据。
   - `bear_history`：追加当前看空论据（独立追踪看空方论据）。
   - `bull_history`：保持不变（从上一轮继承）。
   - `current_response`：更新为当前论据。
   - `count`：递增辩论轮次计数。
7. 返回更新后的 `investment_debate_state`。

## 关键函数/类
- **`create_bear_researcher(llm)`**：工厂函数，返回 `bear_node` 节点。
- **`bear_node(state)`**：LangGraph 节点函数，生成看空论据并更新辩论状态。
  - `state`：需包含 `investment_debate_state`、`market_report`、`sentiment_report`、`news_report`、`fundamentals_report`，可选 `asset_type`。

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.utils.agent_utils`：`get_language_instruction`。
- **被依赖**：
  - 在 LangGraph 图中与 `bull_researcher` 交替执行，构成研究辩论循环。
  - 输出的 `investment_debate_state` 被 `research_manager` 消费以评判辩论结果。
