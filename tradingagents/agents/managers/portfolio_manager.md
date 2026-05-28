# portfolio_manager.py 逻辑说明

## 文件用途
投资组合经理 Agent，作为流水线的最终决策者，综合风险分析师辩论结果、研究计划和交易提案，输出结构化的最终投资组合决策 (PortfolioDecision)。

## 核心逻辑
1. 采用闭包工厂模式：`create_portfolio_manager(llm)` 返回 `portfolio_manager_node(state)` 内部函数。
2. 使用 `deep_thinking_llm`（由调用方传入），通过 `bind_structured()` 尝试绑定结构化输出 schema (`PortfolioDecision`)。
3. 从 `state` 中提取：
   - 风险辩论状态 (`risk_debate_state`)，含完整辩论历史 (`history`) 及各方论据记录。
   - 投资计划 (`investment_plan`)：来自 Research Manager。
   - 交易提案 (`trader_investment_plan`)：来自 Trader。
   - 标的名称 (`company_of_interest`)，用于构建工具上下文。
   - 过往上下文 (`past_context`)：可选，来自记忆模块的历史决策经验。
4. 提示词要求 LLM 扮演投资组合经理，综合风险分析师辩论并做出最终交易决策：
   - 使用 5 级评级体系：Buy / Overweight / Hold / Underweight / Sell。
   - 如果存在过往经验教训 (`past_context`)，将其纳入决策参考。
   - 要求决策果断，每个结论必须基于分析师的具体证据。
5. 通过 `invoke_structured_or_freetext()` 执行 LLM 调用：
   - 优先使用结构化输出（`PortfolioDecision` Pydantic 模型），通过 `render_pm_decision()` 渲染为 Markdown。
   - 渲染结果保持与系统其余部分（记忆日志、CLI 显示、保存报告）一致的 Markdown 格式。
   - 若结构化输出不可用或调用失败，降级为自由文本生成。
6. 更新 `risk_debate_state`：
   - `judge_decision`：设为最终决策。
   - 保留所有历史论据记录。
   - `latest_speaker`：标记为 "Judge"。
   - `count`：不递增（评判不增加辩论轮次）。
7. 输出 `final_trade_decision`（顶层字段），作为整个流水线的最终产出。

## 关键函数/类
- **`create_portfolio_manager(llm)`**：工厂函数，返回 `portfolio_manager_node` 节点。
- **`portfolio_manager_node(state)`**：LangGraph 节点函数，综合辩论并做出最终决策。
  - `state`：需包含 `risk_debate_state`、`investment_plan`、`trader_investment_plan`、`company_of_interest`，可选 `past_context`。
- **结构化输出 schema**：`PortfolioDecision`（来自 `tradingagents.agents.schemas`），包含 `rating`（PortfolioRating）、`executive_summary`（str）、`investment_thesis`（str）、`price_target`（Optional[float]）、`time_horizon`（Optional[str]）。

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.schemas`：`PortfolioDecision`、`render_pm_decision`。
  - `tradingagents.agents.utils.agent_utils`：`build_instrument_context`、`get_language_instruction`。
  - `tradingagents.agents.utils.structured`：`bind_structured`、`invoke_structured_or_freetext`。
- **被依赖**：
  - 输出 `final_trade_decision` 是整个多智能体流水线的最终产物，被报告生成、记忆日志和外部接口消费。
