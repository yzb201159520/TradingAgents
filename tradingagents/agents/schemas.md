# schemas.py 逻辑说明

## 文件用途
定义系统中三个核心决策 Agent（Research Manager、Trader、Portfolio Manager）使用的 Pydantic 结构化输出模型，以及将模型实例渲染回 Markdown 文本的辅助函数。

## 核心逻辑
框架的主要输出仍是自然语言文本（Agent 的推理内容供报告和下游 Agent 阅读）。结构化输出在此基础上叠加，用于：
1. 保证各次运行和不同 LLM 供应商的输出格式一致（节标题统一）。
2. 利用各供应商原生结构化输出模式（OpenAI/xAI 用 json_schema，Gemini 用 response_schema，Anthropic 用 tool-use）。
3. Schema 字段的 `description` 直接作为模型的输出指令，使 prompt 主体可专注于上下文和评级指导。
4. 渲染函数将解析后的 Pydantic 实例转回系统已有的 Markdown 格式，确保显示、记忆日志和保存报告无需改动。

### 评级体系
- **PortfolioRating**（5 级）：Buy / Overweight / Hold / Underweight / Sell — 用于 Research Manager 和 Portfolio Manager。
- **TraderAction**（3 级）：Buy / Hold / Sell — 用于 Trader，将研究计划转化为具体交易方向，仓位调整的精细化由 Portfolio Manager 完成。

## 关键函数/类

### PortfolioRating(str, Enum)
5 级投资评级枚举，从最看涨到最看跌。

### TraderAction(str, Enum)
3 级交易方向枚举，仅表达方向不涉及仓位大小。

### ResearchPlan(BaseModel)
Research Manager 的结构化输出：
- `recommendation: PortfolioRating` — 投资建议评级
- `rationale: str` — 多空辩论要点的自然语言总结
- `strategic_actions: str` — 供 Trader 执行的具体步骤及仓位指导

### render_research_plan(plan) -> str
将 ResearchPlan 渲染为 Markdown，含 **Recommendation**、**Rationale**、**Strategic Actions** 三节。

### TraderProposal(BaseModel)
Trader 的结构化输出：
- `action: TraderAction` — 交易方向
- `reasoning: str` — 基于分析师报告和研究计划的理由
- `entry_price: Optional[float]` — 可选入场目标价
- `stop_loss: Optional[float]` — 可选止损价
- `position_sizing: Optional[str]` — 可选仓位指导（如"5% of portfolio"）

### render_trader_proposal(proposal) -> str
将 TraderProposal 渲染为 Markdown，末尾保留 `FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**` 行以兼容下游停止信号检测。

### PortfolioDecision(BaseModel)
Portfolio Manager 的结构化输出：
- `rating: PortfolioRating` — 最终仓位评级
- `executive_summary: str` — 简明行动计划（入场策略、仓位、关键风险、时间范围）
- `investment_thesis: str` — 基于分析师辩论的详细推理
- `price_target: Optional[float]` — 可选目标价
- `time_horizon: Optional[str]` — 可选持仓周期（如"3-6 months"）

### render_pm_decision(decision) -> str
将 PortfolioDecision 渲染为 Markdown，保留 **Rating**、**Executive Summary**、**Investment Thesis** 节标题以兼容下游解析器。

## 与其他模块的关系
- **依赖**：`pydantic`（BaseModel, Field）
- **被依赖**：
  - `managers/research_manager.py` — 导入 `ResearchPlan`, `render_research_plan`
  - `managers/portfolio_manager.py` — 导入 `PortfolioDecision`, `render_pm_decision`
  - `trader/trader.py` — 导入 `TraderProposal`, `render_trader_proposal`
