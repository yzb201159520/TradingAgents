# analyst_execution.py 逻辑说明

## 文件用途
定义分析师节点的执行计划数据结构和耗时追踪器，为 StateGraph 的动态构建提供节点规格信息，并记录每位分析师的墙钟耗时。

## 核心逻辑

### 分析师节点规格注册
`ANALYST_NODE_SPECS` 字典为四种分析师类型（market / social / news / fundamentals）预定义了固定规格：
- `key` — 分析师标识键（用于工具节点和条件逻辑匹配）
- `agent_node` — 图中智能体节点名称（如 "Market Analyst"）
- `clear_node` — 消息清除节点名称（如 "Msg Clear Market"）
- `tool_node` — 工具节点名称（如 "tools_market"）
- `report_key` — 状态中报告字段的键名（如 "market_report"）

### 执行计划构建
`build_analyst_execution_plan` 根据用户选择的分析师列表，按顺序从 `ANALYST_NODE_SPECS` 中提取规格，组装为 `AnalystExecutionPlan`。该计划同时携带 `concurrency_limit`，供上层控制并行度。

### 墙钟耗时追踪
`AnalystWallTimeTracker` 使用单调时钟（`time.monotonic`）记录每位分析师的开始和完成时间：
- `mark_started(key)` — 标记分析师开始（幂等，仅记录首次）
- `mark_completed(key)` — 标记分析师完成（幂等，仅记录首次）
- `get_wall_times()` — 返回各分析师的耗时字典
- `format_summary()` — 格式化为人类可读的汇总字符串（如 "Market 3.25s | Sentiment 2.10s"）

### 流式追踪同步
`sync_analyst_tracker_from_chunk` 根据图执行的流式 chunk 自动更新追踪器：
- 若 chunk 中已有某分析师的 report → 视为已完成（耗时记为 0）
- 否则，第一个没有 report 的分析师被视为当前活跃节点，标记为已开始

## 关键函数/类

### `AnalystNodeSpec`（frozen dataclass）
- 字段：`key`、`agent_node`、`clear_node`、`tool_node`、`report_key`

### `AnalystExecutionPlan`（frozen dataclass）
- 字段：`specs`（`List[AnalystNodeSpec]`）、`concurrency_limit`

### `build_analyst_execution_plan(selected_analysts, concurrency_limit=1) -> AnalystExecutionPlan`
- 校验分析师键的合法性，确保至少选择一位分析师，返回执行计划。

### `get_initial_analyst_node(plan) -> str`
- 返回计划中第一位分析师的 `agent_node` 名称。

### `AnalystWallTimeTracker`
- 构造参数：`plan: AnalystExecutionPlan`
- 方法：`mark_started`、`mark_completed`、`get_wall_times`、`format_summary`

### `sync_analyst_tracker_from_chunk(tracker, chunk, now=None)`
- 从流式 chunk 同步追踪器状态。

## 与其他模块的关系
- **依赖**：无外部模块依赖（仅使用标准库 `dataclasses`、`time`、`typing`）
- **被依赖**：
  - `setup.py`（调用 `build_analyst_execution_plan` 获取节点规格，用于构建图）
  - `trading_graph.py`（可能使用 `AnalystWallTimeTracker` 记录分析师耗时）
