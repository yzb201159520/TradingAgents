# aggressive_debator.py 逻辑说明

## 文件用途
激进风险分析师 Agent，在风险辩论阶段负责主张高风险高回报策略，积极挑战保守派和中性派的观点，为交易员的决策提供激进维度的论证。

## 核心逻辑
1. 采用闭包工厂模式：`create_aggressive_debator(llm)` 返回 `aggressive_node(state)` 内部函数。
2. 从 `state` 中提取：
   - 风险辩论状态 (`risk_debate_state`)，含辩论历史 (`history`)、激进方历史 (`aggressive_history`)、保守方最新回应 (`current_conservative_response`)、中性方最新回应 (`current_neutral_response`)。
   - 四份分析师报告（`market_report`、`sentiment_report`、`news_report`、`fundamentals_report`）。
   - 交易员决策 (`trader_investment_plan`)。
3. 提示词要求 LLM 扮演激进风险分析师，聚焦以下方面：
   - 积极推崇高回报、高风险机会，强调大胆策略和竞争优势。
   - 关注上行潜力、增长前景和创新收益，即使伴随较高风险。
   - 用数据驱动的反驳质疑保守派和中性派的论点。
   - 指出他们的谨慎可能错失关键机会或假设过于保守。
   - 以对话风格进行辩论式回应，而非单纯呈现数据。
4. 使用 `llm.invoke(prompt)` 单次调用生成论据，将响应格式化为 `"Aggressive Analyst: {response.content}"`。
5. 更新 `risk_debate_state`：
   - `history`：追加当前论据。
   - `aggressive_history`：追加当前论据（独立追踪激进方论据）。
   - `conservative_history` / `neutral_history`：从上一轮继承。
   - `latest_speaker`：标记为 "Aggressive"。
   - `current_aggressive_response`：更新为当前论据。
   - `current_conservative_response` / `current_neutral_response`：从上一轮继承。
   - `count`：递增辩论轮次计数。
6. 返回更新后的 `risk_debate_state`。

## 关键函数/类
- **`create_aggressive_debator(llm)`**：工厂函数，返回 `aggressive_node` 节点。
- **`aggressive_node(state)`**：LangGraph 节点函数，生成激进论据并更新风险辩论状态。
  - `state`：需包含 `risk_debate_state`、`market_report`、`sentiment_report`、`news_report`、`fundamentals_report`、`trader_investment_plan`。

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.utils.agent_utils`：`get_language_instruction`。
- **被依赖**：
  - 在 LangGraph 图中与 `conservative_debator`、`neutral_debator` 轮流执行，构成风险辩论循环。
  - 输出的 `risk_debate_state` 被 `portfolio_manager` 消费以做出最终投资组合决策。
