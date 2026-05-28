# fundamental_data_tools.py 逻辑说明

## 文件用途
定义 4 个 LangChain @tool 装饰的基本面数据获取工具，供基本面分析师 Agent 调用以获取公司财务数据，包括综合基本面、资产负债表、现金流量表和利润表。

## 核心逻辑
所有工具函数遵循统一模式：
1. 使用 `@tool` 装饰器注册为 LangChain 工具，使其可被 ReAct Agent 自动发现和调用。
2. 参数通过 `Annotated[type, description]` 声明，LangChain 将描述提供给 LLM 以辅助工具调用参数生成。
3. 函数本体仅负责参数声明和路由，实际数据获取委托给 `route_to_vendor(tool_name, ...)`，由数据流层根据配置选择具体供应商。

`get_fundamentals` 返回综合基本面报告（一站式），而 `get_balance_sheet`、`get_cashflow`、`get_income_statement` 则针对单项财务报表，均支持年度/季度频率选择。

## 关键函数/类

### get_fundamentals(ticker, curr_date) -> str
- `ticker: str` — 股票代码
- `curr_date: str` — 当前交易日期，yyyy-mm-dd 格式
- 返回综合基本面数据报告
- 路由到 `route_to_vendor("get_fundamentals", ticker, curr_date)`

### get_balance_sheet(ticker, freq="quarterly", curr_date=None) -> str
- `ticker: str` — 股票代码
- `freq: str` — 报告频率，"annual" 或 "quarterly"，默认 "quarterly"
- `curr_date: str` — 当前交易日期，可选
- 返回资产负债表数据报告
- 路由到 `route_to_vendor("get_balance_sheet", ticker, freq, curr_date)`

### get_cashflow(ticker, freq="quarterly", curr_date=None) -> str
- `ticker: str` — 股票代码
- `freq: str` — 报告频率，默认 "quarterly"
- `curr_date: str` — 当前交易日期，可选
- 返回现金流量表数据报告
- 路由到 `route_to_vendor("get_cashflow", ticker, freq, curr_date)`

### get_income_statement(ticker, freq="quarterly", curr_date=None) -> str
- `ticker: str` — 股票代码
- `freq: str` — 报告频率，默认 "quarterly"
- `curr_date: str` — 当前交易日期，可选
- 返回利润表数据报告
- 路由到 `route_to_vendor("get_income_statement", ticker, freq, curr_date)`

## 与其他模块的关系
- **依赖**：
  - `langchain_core.tools.tool` — @tool 装饰器
  - `typing.Annotated` — 参数类型注解
  - `dataflows/interface.route_to_vendor` — 数据供应商路由
- **被依赖**：
  - `utils/agent_utils.py` — 导入全部 4 个工具并重新导出
  - 基本面分析师 Agent 通过 agent_utils 间接使用
