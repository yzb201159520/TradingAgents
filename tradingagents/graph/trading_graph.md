# trading_graph.py 逻辑说明

## 文件用途
TradingAgents 系统的主入口类，组装所有子组件并管理完整的交易分析生命周期——从初始化 LLM 到执行图流水线、记录状态、提取信号、延迟反思。

## 核心逻辑

### 初始化流程
1. 加载配置（默认或自定义），调用 `set_config` 更新全局配置。
2. 创建数据缓存目录和结果目录。
3. 根据 LLM 提供商（Google / OpenAI / Anthropic）注入特定参数（如 thinking_level、reasoning_effort、effort）。
4. 创建深度推理 LLM（deep_thinking_llm）和快速推理 LLM（quick_thinking_llm）。
5. 初始化记忆日志（TradingMemoryLog）。
6. 创建工具节点字典（4 组 ToolNode，分别对应 market / social / news / fundamentals 工具集）。
7. 初始化所有子组件：ConditionalLogic、GraphSetup、Propagator、Reflector、SignalProcessor。
8. 调用 `graph_setup.setup_graph()` 构建 StateGraph 工作流并编译。

### propagate() 主流程
`propagate` 是系统的核心执行入口：
1. **延迟反思处理**：调用 `_resolve_pending_entries`，为同一标的的历史待处理条目获取实际收益并生成反思。
2. **检查点恢复**（可选）：若启用 checkpoint，重新编译带 SqliteSaver 的图，检查是否存在可恢复的检查点。
3. **执行图**：调用 `_run_graph` 运行完整流水线。
4. **清理**：在 finally 块中关闭检查点上下文并恢复无检查点的图编译。

### _run_graph() 图执行流程
1. 从记忆日志获取历史上下文（`past_context`），创建初始状态和图调用参数。
2. 若启用检查点，注入 thread_id 以支持断点续跑。
3. 根据调试模式选择执行方式：
   - **调试模式**：使用 `graph.stream()` 逐节点流式输出，手动合并 chunk 为最终状态。
   - **正常模式**：使用 `graph.invoke()` 一次性执行。
4. 将最终状态存储到 `self.curr_state`。
5. 将状态日志写入磁盘（JSON 文件）。
6. 将决策存入记忆日志（`store_decision`），供未来延迟反思使用。
7. 若启用检查点且执行成功，清除对应检查点。
8. 返回 `(final_state, signal_rating)` 元组。

### _resolve_pending_entries() 延迟反思
处理同一标的的待处理记忆条目：
1. 筛选当前标的的所有 pending 条目。
2. 对每个条目，通过 yfinance 获取持仓期实际收益和超额收益。
3. 若价格数据不可用（日期太近或已退市），跳过并等待下次运行。
4. 调用 Reflector 生成反思文本。
5. 通过 `batch_update_with_outcomes` 原子写入所有更新。

### _resolve_benchmark() 基准标的解析
按优先级选择 alpha 计算的基准：
1. 配置中显式指定的 `benchmark_ticker` 优先级最高。
2. 否则根据标的交易所后缀（如 `.T` 对应东京）匹配 `benchmark_map`。
3. 未匹配的后缀回退到空后缀条目（默认 SPY）。

### _log_state() 状态持久化
将最终状态序列化为 JSON 文件，保存在 `{results_dir}/{ticker}/TradingAgentsStrategy_logs/full_states_log_{date}.json`。标的名称通过 `safe_ticker_component` 净化以防止路径遍历。

## 关键函数/类

### `TradingAgentsGraph`
- **参数**：
  - `selected_analysts` — 选中的分析师列表（默认全部 4 种）
  - `debug` — 调试模式（默认 False）
  - `config` — 配置字典（默认使用 DEFAULT_CONFIG）
  - `callbacks` — 回调处理器列表（用于追踪 LLM/工具统计）

- **主要方法**：
  - `propagate(company_name, trade_date, asset_type="stock")` — 执行完整交易分析流水线，返回 `(final_state, signal_rating)`
  - `process_signal(full_signal)` — 从决策文本提取 5 级评级信号
  - `_run_graph(company_name, trade_date, asset_type)` — 底层图执行逻辑
  - `_resolve_pending_entries(ticker)` — 处理延迟反思
  - `_resolve_benchmark(ticker)` — 解析基准标的
  - `_fetch_returns(ticker, trade_date, holding_days, benchmark)` — 获取实际收益数据
  - `_create_tool_nodes()` — 创建工具节点字典
  - `_get_provider_kwargs()` — 获取 LLM 提供商特定参数
  - `_log_state(trade_date, final_state)` — 持久化状态到磁盘

## 与其他模块的关系
- **依赖**：
  - `langgraph.prebuilt.ToolNode`
  - `tradingagents.llm_clients.create_llm_client`（LLM 客户端创建）
  - `tradingagents.agents`（智能体工厂函数、工具函数）
  - `tradingagents.default_config.DEFAULT_CONFIG`
  - `tradingagents.agents.utils.memory.TradingMemoryLog`（记忆日志）
  - `tradingagents.dataflows.utils.safe_ticker_component`（标的名称净化）
  - `tradingagents.agents.utils.agent_states`（AgentState 等状态类型）
  - `tradingagents.dataflows.config.set_config`（全局配置更新）
  - `.checkpointer`（检查点机制）
  - `.conditional_logic.ConditionalLogic`
  - `.setup.GraphSetup`
  - `.propagation.Propagator`
  - `.reflection.Reflector`
  - `.signal_processing.SignalProcessor`
  - `yfinance`（获取标的和基准价格数据）
- **被依赖**：
  - CLI 入口（`tradingagents/cli/`）
  - API 层或其他上层调用方
