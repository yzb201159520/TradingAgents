# cli/main.py 逻辑说明

## 文件用途
TradingAgents 的 CLI 主入口，基于 Typer 框架构建交互式命令行应用，注册为 `tradingagents` 控制台命令。引导用户选择分析参数，实时展示多智能体交易分析过程和报告。

## 核心逻辑

### 整体流程
1. 用户运行 `tradingagents analyze` 命令（或 `tradingagents` 直接进入）。
2. 通过 `get_user_selections()` 交互式收集所有分析参数（8 步引导流程）。
3. 构建配置字典，初始化 `TradingAgentsGraph`、`StatsCallbackHandler`、`MessageBuffer`。
4. 使用 Rich `Live` 布局以 4fps 刷新率实时展示分析进度。
5. 流式处理图执行输出（`graph.stream()`），逐步更新智能体状态和报告内容。
6. 分析完成后提示用户保存和展示完整报告。

### 交互式引导（8 步）
- Step 1：输入股票代码（自动检测资产类型 — 股票/加密货币）
- Step 2：输入分析日期（YYYY-MM-DD）
- Step 3：选择输出语言
- Step 4：选择分析师团队（Market/Sentiment/News/Fundamentals，加密货币资产自动排除 Fundamentals）
- Step 5：选择研究深度（Shallow=1 / Medium=3 / Deep=5，映射为辩论和风险讨论轮数）
- Step 6：选择 LLM 提供商（11 家：OpenAI/Google/Anthropic/xAI/DeepSeek/Qwen/GLM/MiniMax/OpenRouter/Azure/Ollama），部分提供商需二次选择区域
- Step 7：选择浅层思考和深层思考模型
- Step 8：提供商特定的思考配置（Google thinking_level / OpenAI reasoning_effort / Anthropic effort）

### MessageBuffer 类
核心状态管理类，维护分析过程中的所有实时数据：
- `messages`：消息缓冲区（deque，最多 100 条）
- `tool_calls`：工具调用缓冲区
- `agent_status`：各智能体的状态（pending/in_progress/completed/error）
- `report_sections`：各报告分节内容
- `selected_analysts`：用户选定的分析师列表
- `_processed_message_ids`：消息去重集合

关键设计：
- `REPORT_SECTIONS` 映射定义了每个报告分节对应的分析师键和终结智能体
- `get_completed_reports_count()` 只有当报告有内容 **且** 对应终结智能体完成时才计为完成
- `init_for_analysis()` 根据用户选定的分析师动态构建智能体状态和报告分节

### Rich TUI 布局
五区域布局：
- **header**：欢迎信息
- **progress**（左上）：智能体状态表格，按团队分组显示
- **messages**（右上）：消息和工具调用日志（最新 12 条，倒序）
- **analysis**（下方）：当前报告内容（Markdown 渲染）
- **footer**：统计信息栏（智能体完成数、LLM 调用数、工具调用数、Token 数、报告完成数、耗时）

### 流式处理与状态更新
- 对每个流式 chunk：
  - 消息去重（按 message.id）
  - 分类消息类型（User/Agent/Data/Control/System）
  - 捕获工具调用
  - 更新分析师状态（基于报告内容推断）
  - 处理投资辩论状态（研究团队）
  - 处理交易计划（交易团队）
  - 处理风险辩论状态（风险管理团队和投资组合经理）
- 分析完成后合并所有 chunk 为 `final_state`，调用 `process_signal` 提取最终评级

### 报告保存
`save_report_to_disk()` 将完整报告按五级目录结构保存：
1. `1_analysts/`：各分析师报告
2. `2_research/`：多空辩论和经理决策
3. `3_trading/`：交易计划
4. `4_risk/`：风险团队辩论
5. `5_portfolio/`：投资组合决策
6. `complete_report.md`：合并完整报告

### 日志持久化
通过装饰器模式将 `MessageBuffer` 的 `add_message`、`add_tool_call`、`update_report_section` 方法包装，在内存更新的同时写入磁盘日志和报告文件。

## 关键函数/类

- **`MessageBuffer`**：分析状态缓冲区类，管理智能体状态、消息、工具调用和报告分节
  - `init_for_analysis(selected_analysts)`：根据选定分析师初始化状态
  - `get_completed_reports_count()`：统计已完成报告数
  - `update_report_section(section_name, content)`：更新报告分节并触发显示刷新
- **`create_layout()`**：创建 Rich 五区域 TUI 布局
- **`update_display(layout, spinner_text, stats_handler, start_time)`**：刷新所有布局区域的显示内容
- **`get_user_selections()`**：8 步交互式引导收集所有分析参数
- **`run_analysis(checkpoint)`**：核心分析执行函数，包含配置构建、图初始化、流式处理、报告保存
- **`update_analyst_statuses(message_buffer, chunk, wall_time_tracker)`**：基于 chunk 数据更新分析师状态
- **`classify_message_type(message)`**：将 LangChain 消息分类为 User/Agent/Data/Control/System
- **`extract_content_string(content)`**：从多种消息格式中提取文本内容
- **`save_report_to_disk(final_state, ticker, save_path)`**：将分析报告保存为分层目录结构
- **`display_complete_report(final_state)`**：在终端完整显示分析报告
- **`analyze(checkpoint, clear_checkpoints)`**：Typer 命令入口，处理检查点清理后调用 `run_analysis`

## 与其他模块的关系
- **依赖**：
  - `tradingagents.graph.trading_graph.TradingAgentsGraph`：核心交易图
  - `tradingagents.graph.analyst_execution`：分析师执行计划（`build_analyst_execution_plan`、`AnalystWallTimeTracker` 等）
  - `tradingagents.default_config.DEFAULT_CONFIG`：默认配置
  - `cli.models.AnalystType`：分析师类型枚举
  - `cli.utils`：CLI 工具函数（股票代码输入、提供商选择、API Key 确保等）
  - `cli.announcements`：公告获取和显示
  - `cli.stats_handler.StatsCallbackHandler`：LLM/工具调用统计回调
  - `rich`：TUI 渲染库（Console、Panel、Layout、Live、Table、Markdown 等）
  - `typer`：CLI 框架
  - `questionary`：交互式问答
- **被依赖**：
  - 通过 `pyproject.toml` 注册为 `tradingagents` 控制台命令入口点（`cli.main:app`）
