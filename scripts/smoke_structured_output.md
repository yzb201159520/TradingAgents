# scripts/smoke_structured_output.py 逻辑说明

## 文件用途
结构化输出的端到端冒烟测试脚本，直接运行三个决策智能体（Research Manager、Trader、Portfolio Manager）及其结构化输出绑定，验证各 LLM 提供商的原生结构化输出模式能正确返回符合预期 Schema 的 Pydantic 实例。

## 核心逻辑

### 整体流程
1. 从命令行参数获取 LLM 提供商名称（openai/google/anthropic/deepseek/qwen/glm/xai）。
2. 可选覆盖 deep/quick 模型（`--deep-model`、`--quick-model`），默认使用 `PROVIDER_DEFAULTS` 中的预设模型。
3. 通过 `create_llm_client` 工厂创建 LLM 客户端实例。
4. 按顺序执行三个结构化输出智能体：
   - **Research Manager**：输入辩论状态，输出投资计划（`investment_plan`）
   - **Trader**：输入投资计划，输出交易计划（`trader_investment_plan`）
   - **Portfolio Manager**：输入投资计划和交易计划，输出最终交易决策（`final_trade_decision`）
5. 使用 `SignalProcessor`（零 LLM 调用）从最终决策中提取评级。
6. 执行结构检查：验证每个智能体输出包含必需的 Markdown 段标记（如 `**Recommendation**:`、`**Rating**:` 等）。
7. 根据检查结果返回 0（通过）或 1（失败）。

### 测试数据构造
- `_make_rm_state()`：构造 Research Manager 所需的最小化但真实的状态（NVDA 辩论历史）
- `_make_trader_state(investment_plan)`：构造 Trader 所需的状态
- `_make_pm_state(investment_plan, trader_plan)`：构造 Portfolio Manager 所需的状态（含风险辩论状态和各分析师报告）

### 设计要点
- 不调用 `propagate()`，仅测试三个结构化输出调用和 SignalProcessor，控制测试表面积和成本
- 支持多种提供商的结构化输出模式：OpenAI/xAI/DeepSeek/Qwen/GLM 使用 json_schema、Gemini 使用 response_schema、Anthropic 使用 tool-use
- 每个智能体的输出同时打印 Pydantic 实例和渲染后的 Markdown

## 关键函数/类

- **`main() -> int`**：主入口函数，执行冒烟测试流程
- **`_make_rm_state() -> dict`**：构造 Research Manager 测试状态
- **`_make_trader_state(investment_plan) -> dict`**：构造 Trader 测试状态
- **`_make_pm_state(investment_plan, trader_plan) -> dict`**：构造 Portfolio Manager 测试状态
- **`_print_section(title, content) -> None`**：格式化打印测试结果段落

### 常量
- **`PROVIDER_DEFAULTS`**：各提供商的默认模型映射
  - openai: gpt-5.4-mini / google: gemini-2.5-flash / anthropic: claude-sonnet-4-6 / deepseek: deepseek-chat / qwen: qwen-plus / glm: glm-5 / xai: grok-4

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.managers.portfolio_manager.create_portfolio_manager`：Portfolio Manager 智能体
  - `tradingagents.agents.managers.research_manager.create_research_manager`：Research Manager 智能体
  - `tradingagents.agents.trader.trader.create_trader`：Trader 智能体
  - `tradingagents.graph.signal_processing.SignalProcessor`：信号处理器（从决策文本提取评级）
  - `tradingagents.llm_clients.create_llm_client`：LLM 客户端工厂
- **被依赖**：无（独立冒烟测试脚本）
