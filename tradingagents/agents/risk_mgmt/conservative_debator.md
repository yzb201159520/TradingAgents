# conservative_debator.py 逻辑说明

## 文件用途
保守风险分析师 Agent，在风险辩论阶段负责主张低风险稳健策略，积极挑战激进派和中性派的观点，为交易员的决策提供保守维度的论证。

## 核心逻辑
1. 采用闭包工厂模式：`create_conservative_debator(llm)` 返回 `conservative_node(state)` 内部函数。
2. 从 `state` 中提取：
   - 风险辩论状态 (`risk_debate_state`)，含辩论历史 (`history`)、保守方历史 (`conservative_history`)、激进方最新回应 (`current_aggressive_response`)、中性方最新回应 (`current_neutral_response`)。
   - 四份分析师报告（`market_report`、`sentiment_report`、`news_report`、`fundamentals_report`）。
   - 交易员决策 (`trader_investment_plan`)。
3. 提示词要求 LLM 扮演保守风险分析师，聚焦以下方面：
   - 首要目标是保护资产、最小化波动、确保稳定可靠增长。
   - 优先考虑稳定性、安全性和风险缓解，仔细评估潜在损失、经济衰退和市场波动。
   - 批判性审查高风险因素，指出交易决策可能带来的过度风险暴露。
   - 积极反驳激进派和中性派的论点，指出他们可能忽视的潜在威胁或未优先考虑可持续性。
   - 以对话风格质疑对方的乐观假设，强调他们可能忽略的下行风险。
4. 使用 `llm.invoke(prompt)` 单次调用生成论据，将响应格式化为 `"Conservative Analyst: {response.content}"`。
5. 更新 `risk_debate_state`：
   - `history`：追加当前论据。
   - `conservative_history`：追加当前论据（独立追踪保守方论据）。
   - `aggressive_history` / `neutral_history`：从上一轮继承。
   - `latest_speaker`：标记为 "Conservative"。
   - `current_conservative_response`：更新为当前论据。
   - `current_aggressive_response` / `current_neutral_response`：从上一轮继承。
   - `count`：递增辩论轮次计数。
6. 返回更新后的 `risk_debate_state`。

## 关键函数/类
- **`create_conservative_debator(llm)`**：工厂函数，返回 `conservative_node` 节点。
- **`conservative_node(state)`**：LangGraph 节点函数，生成保守论据并更新风险辩论状态。
  - `state`：需包含 `risk_debate_state`、`market_report`、`sentiment_report`、`news_report`、`fundamentals_report`、`trader_investment_plan`。

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.utils.agent_utils`：`get_language_instruction`。
- **被依赖**：
  - 在 LangGraph 图中与 `aggressive_debator`、`neutral_debator` 轮流执行，构成风险辩论循环。
  - 输出的 `risk_debate_state` 被 `portfolio_manager` 消费以做出最终投资组合决策。
