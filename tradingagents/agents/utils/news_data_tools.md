# news_data_tools.py 逻辑说明

## 文件用途
定义 3 个 LangChain @tool 装饰的新闻数据获取工具，供新闻分析师和情绪分析师 Agent 调用，包括个股新闻、全球宏观新闻和内部人交易数据。

## 核心逻辑
所有工具函数遵循统一模式：使用 `@tool` 注册为 LangChain 工具，参数通过 `Annotated` 声明描述信息，函数本体将请求委托给 `route_to_vendor(tool_name, ...)` 进行数据路由。

### 个股新闻 vs 全球新闻的分工
- `get_news` 针对特定标的获取相关新闻，需要指定日期范围。
- `get_global_news` 获取宏观层面的全球新闻，仅需当前日期，回看天数和文章数量上限可从全局配置继承或显式覆盖。

### 内部人交易
`get_insider_transactions` 提供公司内部人买卖记录，帮助 Agent 判断管理层对自身股票的态度。

## 关键函数/类

### get_news(ticker, start_date, end_date) -> str
- `ticker: str` — 股票代码
- `start_date: str` — 起始日期，yyyy-mm-dd 格式
- `end_date: str` — 结束日期，yyyy-mm-dd 格式
- 返回个股新闻数据字符串
- 路由到 `route_to_vendor("get_news", ticker, start_date, end_date)`

### get_global_news(curr_date, look_back_days=None, limit=None) -> str
- `curr_date: str` — 当前日期，yyyy-mm-dd 格式
- `look_back_days: Optional[int]` — 回看天数，未指定时使用配置默认值（`global_news_lookback_days`）
- `limit: Optional[int]` — 最大返回文章数，未指定时使用配置默认值（`global_news_article_limit`）
- 返回全球新闻数据字符串
- 路由到 `route_to_vendor("get_global_news", curr_date, look_back_days, limit)`

### get_insider_transactions(ticker) -> str
- `ticker: str` — 股票代码
- 返回公司内部人交易数据报告
- 路由到 `route_to_vendor("get_insider_transactions", ticker)`

## 与其他模块的关系
- **依赖**：
  - `langchain_core.tools.tool` — @tool 装饰器
  - `typing.Annotated, Optional` — 参数类型注解
  - `dataflows/interface.route_to_vendor` — 数据供应商路由
- **被依赖**：
  - `utils/agent_utils.py` — 导入全部 3 个工具并重新导出
  - 新闻分析师、情绪分析师 Agent 通过 agent_utils 间接使用
