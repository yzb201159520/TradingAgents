# propagation.py 逻辑说明

## 文件用途
负责创建图的初始状态和调用参数，是图执行前的状态初始化入口。

## 核心逻辑

### 初始状态创建
`create_initial_state` 方法构建 `AgentState` 的完整初始值：

1. **消息**：以 `("human", company_name)` 作为初始人类消息，触发分析师节点启动。
2. **元信息**：设置 `company_of_interest`（目标公司）、`asset_type`（资产类型，默认 "stock"）、`trade_date`（交易日期）、`past_context`（历史上下文，来自记忆日志）。
3. **投资辩论状态**：初始化 `InvestDebateState`，所有历史和计数字段置空或归零。
4. **风险辩论状态**：初始化 `RiskDebateState`，所有历史、发言者和计数字段置空或归零。
5. **分析师报告**：`market_report`、`fundamentals_report`、`sentiment_report`、`news_report` 均初始化为空字符串，等待分析师节点填充。

### 图调用参数
`get_graph_args` 方法返回图执行所需的参数字典：
- `stream_mode: "values"` — 以值模式流式输出
- `config.recursion_limit` — 最大递归限制（默认 100），防止单次执行中图循环次数过多
- `config.callbacks` — 可选的回调处理器列表（用于工具执行追踪等）

## 关键函数/类

### `Propagator`
- **参数**：`max_recur_limit`（最大递归限制，默认 100）
- **方法**：
  - `create_initial_state(company_name, trade_date, asset_type="stock", past_context="") -> Dict[str, Any]` — 创建完整初始状态
  - `get_graph_args(callbacks=None) -> Dict[str, Any]` — 返回图调用参数

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.utils.agent_states`（`AgentState`、`InvestDebateState`、`RiskDebateState` 类型定义）
- **被依赖**：
  - `trading_graph.py`（TradingAgentsGraph 在 `_run_graph` 中调用 `propagator.create_initial_state()` 和 `propagator.get_graph_args()`）
