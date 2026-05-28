# neutral_debator.py 逻辑说明

## 文件用途
中性风险分析师 Agent，在风险辩论阶段负责提供平衡视角，同时挑战激进派和保守派的极端观点，为交易员的决策提供中性维度的论证。

## 核心逻辑
1. 采用闭包工厂模式：`create_neutral_debator(llm)` 返回 `neutral_node(state)` 内部函数。
2. 从 `state` 中提取：
   - 风险辩论状态 (`risk_debate_state`)，含辩论历史 (`history`)、中性方历史 (`neutral_history`)、激进方最新回应 (`current_aggressive_response`)、保守方最新回应 (`current_conservative_response`)。
   - 四份分析师报告（`market_report`、`sentiment_report`、`news_report`、`fundamentals_report`）。
   - 交易员决策 (`trader_investment_plan`)。
3. 提示词要求 LLM 扮演中性风险分析师，聚焦以下方面：
   - 提供平衡视角，权衡潜在收益与风险。
   - 优先考虑全面方法，评估上行和下行空间，同时考虑更广泛的市场趋势、潜在经济变化和多元化策略。
   - 挑战激进派和保守派，指出各自的过度乐观或过度谨慎之处。
   - 倡导温和、可持续的策略调整。
   - 分析双方论点的弱点，主张适度风险策略可以在提供增长潜力的同时防范极端波动。
4. 使用 `llm.invoke(prompt)` 单次调用生成论据，将响应格式化为 `"Neutral Analyst: {response.content}"`。
5. 更新 `risk_debate_state`：
   - `history`：追加当前论据。
   - `neutral_history`：追加当前论据（独立追踪中性方论据）。
   - `aggressive_history` / `conservative_history`：从上一轮继承。
   - `latest_speaker`：标记为 "Neutral"。
   - `current_neutral_response`：更新为当前论据。
   - `current_aggressive_response` / `current_conservative_response`：从上一轮继承。
   - `count`：递增辩论轮次计数。
6. 返回更新后的 `risk_debate_state`。

## 关键函数/类
- **`create_neutral_debator(llm)`**：工厂函数，返回 `neutral_node` 节点。
- **`neutral_node(state)`**：LangGraph 节点函数，生成中性论据并更新风险辩论状态。
  - `state`：需包含 `risk_debate_state`、`market_report`、`sentiment_report`、`news_report`、`fundamentals_report`、`trader_investment_plan`。

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.utils.agent_utils`：`get_language_instruction`。
- **被依赖**：
  - 在 LangGraph 图中与 `aggressive_debator`、`conservative_debator` 轮流执行，构成风险辩论循环。
  - 输出的 `risk_debate_state` 被 `portfolio_manager` 消费以做出最终投资组合决策。
