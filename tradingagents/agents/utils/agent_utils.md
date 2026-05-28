# agent_utils.py 逻辑说明

## 文件用途
为 Agent 层提供数据工具的统一导入入口、语言指令生成函数、金融标的上下文构建函数，以及消息清除回调工厂函数。

## 核心逻辑

### 工具导入聚合
从各专用工具模块（core_stock_tools、technical_indicators_tools、fundamental_data_tools、news_data_tools）导入所有 LangChain @tool 工具函数，使上层 Agent 可从 `agent_utils` 统一引用，无需关心工具文件的组织细节。

### 输出语言控制
`get_language_instruction()` 从全局配置读取 `output_language`，若非英语则返回提示指令片段（如"Write your entire response in Chinese."），注入到每个 Agent 的 prompt 中实现全链路本地化输出。英语时返回空串以节省 token。

### 标的上下文构建
`build_instrument_context()` 根据资产类型（stock/crypto）生成描述当前分析标的的 prompt 片段，提醒 Agent 保留交易所后缀（如 .TO、.L、-USD），对加密资产特别标注不应假设公司基本面数据可用。

### 消息清除
`create_msg_delete()` 返回一个回调函数，用于在 LangGraph 状态图中清除当前节点的所有消息并插入一个占位消息（"Continue"），主要解决 Anthropic API 不允许空消息列表的兼容性问题。

## 关键函数/类

### get_language_instruction() -> str
- 无参数
- 返回语言提示指令字符串，英语时为空串

### build_instrument_context(ticker, asset_type="stock") -> str
- `ticker: str` — 标的代码
- `asset_type: str` — 资产类型，"stock" 或 "crypto"
- 返回描述标的的 prompt 片段

### create_msg_delete() -> Callable
- 无参数
- 返回 `delete_messages(state)` 回调函数，该回调接收 state 字典，移除所有消息并添加占位消息

## 与其他模块的关系
- **依赖**：
  - `langchain_core.messages`（HumanMessage, RemoveMessage）
  - `utils/core_stock_tools` — get_stock_data
  - `utils/technical_indicators_tools` — get_indicators
  - `utils/fundamental_data_tools` — get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement
  - `utils/news_data_tools` — get_news, get_insider_transactions, get_global_news
  - `dataflows/config` — get_config（延迟导入）
- **被依赖**：
  - 所有分析师、研究员、辩论者、经理、交易员 Agent 模块均从此处导入 `get_language_instruction`、工具函数和 `create_msg_delete`
  - `graph/trading_graph.py` — 导入 `create_msg_delete`, `get_language_instruction`, `build_instrument_context`
