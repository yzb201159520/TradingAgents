# trader.py 逻辑说明

## 文件用途
交易员 Agent，负责将研究经理的投资计划转化为具体的结构化交易提案 (TraderProposal)，包含买卖方向、入场价、止损价和仓位大小。

## 核心逻辑
1. 采用闭包工厂模式：`create_trader(llm)` 返回 `functools.partial(trader_node, name="Trader")`。
2. 使用 `deep_thinking_llm`（由调用方传入），通过 `bind_structured()` 尝试绑定结构化输出 schema (`TraderProposal`)。
3. 从 `state` 中提取：
   - 标的名称 (`company_of_interest`) 和资产类型 (`asset_type`)，用于构建工具上下文。
   - 投资计划 (`investment_plan`)，作为交易决策的基础输入。
4. 组装系统消息和用户消息：
   - 系统消息：定义角色为交易代理，要求基于分析师报告和研究计划提供具体的买/卖/持有建议。
   - 用户消息：包含标的名称、工具上下文和投资计划原文。
5. 通过 `invoke_structured_or_freetext()` 执行 LLM 调用：
   - 优先使用结构化输出（`TraderProposal` Pydantic 模型），通过 `render_trader_proposal()` 渲染为 Markdown。
   - 渲染结果末尾保留 `FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**` 行，用于向后兼容分析师停止信号。
   - 若结构化输出不可用或调用失败，降级为自由文本生成。
6. 返回更新后的 `messages`（AIMessage）、`trader_investment_plan` 和 `sender`（固定为 "Trader"）。

## 关键函数/类
- **`create_trader(llm)`**：工厂函数，返回带 `name="Trader"` 参数的 `trader_node` 偏函数。
- **`trader_node(state, name)`**：LangGraph 节点函数，生成交易提案。
  - `state`：需包含 `company_of_interest`、`investment_plan`，可选 `asset_type`。
  - `name`：发送者标识，由偏函数固定为 "Trader"。
- **结构化输出 schema**：`TraderProposal`（来自 `tradingagents.agents.schemas`），包含 `action`（TraderAction: Buy/Hold/Sell）、`reasoning`（str）、`entry_price`（Optional[float]）、`stop_loss`（Optional[float]）、`position_sizing`（Optional[str]）。

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.schemas`：`TraderProposal`、`render_trader_proposal`。
  - `tradingagents.agents.utils.agent_utils`：`build_instrument_context`、`get_language_instruction`。
  - `tradingagents.agents.utils.structured`：`bind_structured`、`invoke_structured_or_freetext`。
  - `langchain_core.messages`：`AIMessage`。
  - `functools`：`partial`。
- **被依赖**：
  - 输出 `trader_investment_plan` 被三个 Risk Debator（Aggressive/Conservative/Neutral）消费，作为辩论主题。
