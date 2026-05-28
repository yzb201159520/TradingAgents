# main.py 逻辑说明

## 文件用途
TradingAgents 项目的编程式入口，以脚本方式创建交易分析图并执行前向传播，生成交易决策。

## 核心逻辑
1. 从 `default_config` 获取默认配置（`DEFAULT_CONFIG`），该配置已自动应用 `TRADINGAGENTS_*` 环境变量覆盖（如 `llm_provider`、`deep_think_llm`、`quick_think_llm`、`backend_url` 等），因此用户可以通过 `.env` 切换模型或端点，无需修改脚本。
2. 以 `debug=True` 和自定义配置初始化 `TradingAgentsGraph` 实例。
3. 调用 `ta.propagate("NVDA", "2024-05-10")` 对指定股票和日期执行完整的多智能体分析流程，返回最终状态和交易决策。
4. 打印交易决策结果。
5. 注释中保留了 `ta.reflect_and_remember(1000)` 调用，用于记忆错误和反思（参数为持仓收益率），当前未启用。

## 关键函数/类
- 无自定义函数/类，整个文件为顶层脚本，直接执行分析流程。

## 与其他模块的关系
- **依赖**：
  - `tradingagents.graph.trading_graph.TradingAgentsGraph`：核心交易图，执行多智能体传播
  - `tradingagents.default_config.DEFAULT_CONFIG`：默认配置字典
- **被依赖**：无（作为独立入口脚本使用）
