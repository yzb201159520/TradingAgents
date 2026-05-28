# memory.py 逻辑说明

## 文件用途
实现 `TradingMemoryLog`——一个仅追加的 Markdown 格式交易决策日志，支持两阶段（Phase A 决策存储 + Phase B 延迟反思更新）工作流，为 Agent 提供历史分析和反思的上下文记忆。

## 核心逻辑

### 两阶段工作流

**Phase A — 决策存储（propagate 阶段）**
- `store_decision()` 在每次交易决策后追加一条"待定"（pending）条目到日志文件，包含日期、标的、评级和决策文本，不触发 LLM 调用。
- 幂等性保护：在写入前扫描文件，若发现相同 `[trade_date | ticker | rating | pending]` 标签则跳过，防止重复写入。

**Phase B — 延迟反思更新（回测阶段）**
- `update_with_outcome()` 在持有期结束后，找到匹配的 pending 条目，更新标签（加入实际收益率和持仓天数），追加 REFLECTION 节。
- 使用原子写入（临时文件 + `os.replace()`），确保崩溃不会损坏日志。
- `batch_update_with_outcomes()` 支持批量更新，通过 O(1) 查找表优化多条目同时更新。

### 日志格式
每条日志条目以标签行开头：`[date | ticker | rating | raw_return | alpha_return | holding_days]`（pending 状态为 `[date | ticker | rating | pending]`），后跟 `DECISION:` 和可选的 `REFLECTION:` 节。条目之间以 HTML 注释 `<!-- ENTRY_END -->` 分隔（此标记不可能出现在 LLM 文本输出中，是安全的硬分隔符）。

### 上下文注入
`get_past_context()` 为 Agent prompt 提供历史记忆：
- 优先返回同一标的的最近 N 条完整分析（含决策和反思）
- 补充跨标的的最近 M 条反思摘要（仅反思部分，决策截断到 300 字符）
- 通过 `n_same` 和 `n_cross` 参数控制各类条目数量

### 条目轮转
`_apply_rotation()` 在已解决条目数量超过 `memory_log_max_entries` 配置时，丢弃最旧的已解决条目，pending 条目始终保留。

### 正则解析
预编译 `_DECISION_RE` 和 `_REFLECTION_RE` 正则，避免每次 `load_entries()` 调用时重复编译。

## 关键函数/类

### TradingMemoryLog
构造参数：
- `config: dict` — 配置字典，可包含 `memory_log_path`（日志文件路径）和 `memory_log_max_entries`（最大已解决条目数）

#### store_decision(ticker, trade_date, final_trade_decision) -> None
- `ticker: str` — 标的代码
- `trade_date: str` — 交易日期
- `final_trade_decision: str` — 决策文本
- 追加 pending 条目到日志文件，带幂等性保护

#### load_entries() -> List[dict]
- 解析日志文件所有条目，返回字典列表
- 每个字典含 date, ticker, rating, pending, raw, alpha, holding, decision, reflection 字段

#### get_pending_entries() -> List[dict]
- 返回所有 pending 状态的条目（供 Phase B 处理）

#### get_past_context(ticker, n_same=5, n_cross=3) -> str
- `ticker: str` — 当前分析标的
- `n_same: int` — 同标的最多返回条数，默认 5
- `n_cross: int` — 跨标的最多返回条数，默认 3
- 返回格式化的历史上下文字符串，直接注入 Agent prompt

#### update_with_outcome(ticker, trade_date, raw_return, alpha_return, holding_days, reflection) -> None
- 更新匹配的 pending 条目为已解决状态，追加 REFLECTION 节
- 使用原子写入

#### batch_update_with_outcomes(updates) -> None
- `updates: List[dict]` — 每个元素须含 ticker, trade_date, raw_return, alpha_return, holding_days, reflection 键
- 单次读取 + 原子写入完成批量更新

#### _apply_rotation(blocks) -> List[str]
- 内部方法，超出上限时丢弃最旧已解决条目

#### _parse_entry(raw) -> Optional[dict]
- 内部方法，解析单条原始文本为字典

#### _format_full(e) -> str / _format_reflection_only(e) -> str
- 内部方法，格式化条目为完整/仅反思的文本

## 与其他模块的关系
- **依赖**：
  - `utils/rating.py` — 导入 `parse_rating`，用于从决策文本提取评级
  - `pathlib.Path`, `re`, `typing.List`, `typing.Optional` — 标准库
- **被依赖**：
  - `graph/trading_graph.py` — 导入 `TradingMemoryLog`，在图构建中实例化并注入各节点
