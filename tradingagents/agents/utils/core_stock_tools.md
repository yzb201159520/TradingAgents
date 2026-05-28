# core_stock_tools.py 逻辑说明

## 文件用途
定义 LangChain @tool 装饰的股票价格数据获取工具 `get_stock_data`，供市场分析师等 Agent 调用以获取 OHLCV（开高低收量）行情数据。

## 核心逻辑
使用 `@tool` 装饰器将普通 Python 函数注册为 LangChain 工具，使其可被 ReAct Agent 自动发现和调用。函数本身仅负责参数声明和路由，实际数据获取委托给 `route_to_vendor("get_stock_data", ...)`，由数据流层根据配置选择具体供应商（如 Yahoo Finance、Financial Modeling Prep 等）。

参数通过 `Annotated[type, description]` 形式声明，LangChain 会将这些描述提供给 LLM，帮助模型正确生成工具调用参数。

## 关键函数/类

### get_stock_data(symbol, start_date, end_date) -> str
- `symbol: str` — 股票代码，如 AAPL、TSM
- `start_date: str` — 起始日期，yyyy-mm-dd 格式
- `end_date: str` — 结束日期，yyyy-mm-dd 格式
- 返回格式化的 DataFrame 字符串，包含指定日期范围内的 OHLCV 数据
- 内部调用 `route_to_vendor("get_stock_data", symbol, start_date, end_date)`

## 与其他模块的关系
- **依赖**：
  - `langchain_core.tools.tool` — @tool 装饰器
  - `typing.Annotated` — 参数类型注解
  - `dataflows/interface.route_to_vendor` — 数据供应商路由
- **被依赖**：
  - `utils/agent_utils.py` — 导入 get_stock_data 并重新导出
  - 各分析师 Agent 通过 agent_utils 间接使用
