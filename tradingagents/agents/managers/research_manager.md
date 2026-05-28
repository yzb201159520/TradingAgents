# research_manager.py 逻辑说明

## 文件用途
研究经理 Agent，负责评判看多/看空辩论结果，将辩论历史综合为结构化的投资研究计划 (ResearchPlan)，传递给交易员执行。

## 核心逻辑
1. 采用闭包工厂模式：`create_research_manager(llm)` 返回 `research_manager_node(state)` 内部函数。
2. 使用 `deep_thinking_llm`（由调用方传入），通过 `bind_structured()` 尝试绑定结构化输出 schema (`ResearchPlan`)。
3. 从 `state` 中提取：
   - 辩论状态 (`investment_debate_state`)，含辩论历史 (`history`)。
   - 标的名称 (`company_of_interest`)，用于构建工具上下文。
4. 提示词要求 LLM 扮演研究经理和辩论主持人，评价辩论并输出明确的投资计划：
   - 使用 5 级评级体系：Buy / Overweight / Hold / Underweight / Sell。
   - 当论据明显偏向一方时做出明确判断，仅在双方证据真正均衡时使用 Hold。
5. 通过 `invoke_structured_or_freetext()` 执行 LLM 调用：
   - 优先使用结构化输出（`ResearchPlan` Pydantic 模型），通过 `render_research_plan()` 渲染为 Markdown。
   - 若结构化输出不可用或调用失败，降级为自由文本生成。
6. 更新 `investment_debate_state`：
   - `judge_decision`：设为生成的投资计划。
   - 保留原始 `history`、`bull_history`、`bear_history`、`count`。
   - `current_response`：更新为投资计划。
7. 同时输出 `investment_plan`（顶层字段），供 Trader 直接读取。

## 关键函数/类
- **`create_research_manager(llm)`**：工厂函数，返回 `research_manager_node` 节点。
- **`research_manager_node(state)`**：LangGraph 节点函数，评判辩论并生成投资计划。
  - `state`：需包含 `investment_debate_state`、`company_of_interest`。
- **结构化输出 schema**：`ResearchPlan`（来自 `tradingagents.agents.schemas`），包含 `recommendation`（PortfolioRating）、`rationale`（str）、`strategic_actions`（str）。

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.schemas`：`ResearchPlan`、`render_research_plan`。
  - `tradingagents.agents.utils.agent_utils`：`build_instrument_context`、`get_language_instruction`。
  - `tradingagents.agents.utils.structured`：`bind_structured`、`invoke_structured_or_freetext`。
- **被依赖**：
  - 输出 `investment_plan` 被 `trader` 消费，作为交易决策的基础。
  - 输出 `investment_debate_state` 在图状态中保留辩论记录。
