# bull_researcher.py 逻辑说明

## 文件用途
看多研究员 Agent，在研究辩论阶段负责基于分析师报告构建看多论据，与看空研究员进行交替辩论。

## 核心逻辑
1. 采用闭包工厂模式：`create_bull_researcher(llm)` 返回 `bull_node(state)` 内部函数。
2. 从 `state` 中提取辩论状态 (`investment_debate_state`) 和四份分析师报告（`market_report`、`sentiment_report`、`news_report`、`fundamentals_report`）。
3. 根据资产类型 (`asset_type`) 动态调整提示词标签（stock → "stock"/"Company fundamentals report"，crypto → "asset"/"Asset fundamentals report"）。
4. 提示词要求 LLM 扮演看多分析师，聚焦以下方面：
   - 增长潜力：市场机会、收入预期、可扩展性。
   - 竞争优势：独特产品、品牌力、市场地位。
   - 正面指标：财务健康、行业趋势、利好新闻。
   - 反驳看空论点：用具体数据回应看空方关切。
   - 互动式辩论风格：而非单纯罗列数据。
5. 使用 `llm.invoke(prompt)` 单次调用生成论据，将响应格式化为 `"Bull Analyst: {response.content}"`。
6. 更新 `investment_debate_state`：
   - `history`：追加当前看多论据。
   - `bull_history`：追加当前看多论据（独立追踪看多方论据）。
   - `bear_history`：保持不变（从上一轮继承）。
   - `current_response`：更新为当前论据。
   - `count`：递增辩论轮次计数。
7. 返回更新后的 `investment_debate_state`。

## 关键函数/类
- **`create_bull_researcher(llm)`**：工厂函数，返回 `bull_node` 节点。
- **`bull_node(state)`**：LangGraph 节点函数，生成看多论据并更新辩论状态。
  - `state`：需包含 `investment_debate_state`、`market_report`、`sentiment_report`、`news_report`、`fundamentals_report`，可选 `asset_type`。

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.utils.agent_utils`：`get_language_instruction`。
- **被依赖**：
  - 在 LangGraph 图中与 `bear_researcher` 交替执行，构成研究辩论循环。
  - 输出的 `investment_debate_state` 被 `research_manager` 消费以评判辩论结果。
