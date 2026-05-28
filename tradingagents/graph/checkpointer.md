# checkpointer.py 逻辑说明

## 文件用途
提供基于 SQLite 的 LangGraph 检查点机制，支持交易分析流程的中断恢复，使崩溃的运行可以从上一个成功节点继续执行。

## 核心逻辑

### 每标的独立数据库
为避免并发标的之间的写入冲突，每个标的（ticker）使用独立的 SQLite 数据库文件。数据库文件存放在 `{data_dir}/checkpoints/{TICKER}.db` 路径下。

### 线程 ID 确定性
`thread_id` 函数使用 SHA-256 哈希的 前 16 位十六进制字符 作为线程 ID，确保同一标的+日期组合始终映射到同一线程，从而实现断点续跑；不同日期则启动新线程。

### 检查点生命周期
1. **启用**：当配置中 `checkpoint_enabled` 为 True 时，`propagate` 方法将工作流重新编译为带 SqliteSaver 的图。
2. **恢复**：运行前检查是否有现存检查点（`checkpoint_step`），若有则从该步骤继续。
3. **清除**：成功完成后自动清除检查点（`clear_checkpoint`），避免过期状态影响后续运行。
4. **批量清除**：`clear_all_checkpoints` 可删除所有检查点数据库文件。

### 安全性
- 标的名称通过 `safe_ticker_component` 净化，防止路径遍历攻击。
- `get_checkpointer` 使用上下文管理器模式，确保数据库连接在使用后正确关闭。

## 关键函数/类

### `_db_path(data_dir, ticker) -> Path`
- 根据数据目录和标的名称计算 SQLite 数据库文件路径，自动创建 checkpoints 目录。

### `thread_id(ticker, date) -> str`
- 根据标的和日期生成确定性的 16 位十六进制线程 ID。

### `get_checkpointer(data_dir, ticker) -> Generator[SqliteSaver]`
- 上下文管理器，创建并初始化 SqliteSaver 实例，退出时关闭数据库连接。

### `has_checkpoint(data_dir, ticker, date) -> bool`
- 判断指定标的+日期是否存在可恢复的检查点。

### `checkpoint_step(data_dir, ticker, date) -> int | None`
- 返回最新检查点的步骤编号，若无则返回 None。

### `clear_all_checkpoints(data_dir) -> int`
- 删除所有检查点数据库文件，返回删除文件数量。

### `clear_checkpoint(data_dir, ticker, date) -> None`
- 删除指定标的+日期的检查点数据（从 writes 和 checkpoints 表中删除对应线程 ID 的行）。

## 与其他模块的关系
- **依赖**：
  - `langgraph.checkpoint.sqlite.SqliteSaver`（LangGraph 的 SQLite 检查点持久化实现）
  - `tradingagents.dataflows.utils.safe_ticker_component`（标的名称净化）
  - 标准库 `sqlite3`、`hashlib`、`pathlib`
- **被依赖**：
  - `trading_graph.py`（TradingAgentsGraph 在 `propagate` 和 `_run_graph` 中调用 `get_checkpointer`、`checkpoint_step`、`clear_checkpoint`、`thread_id`）
