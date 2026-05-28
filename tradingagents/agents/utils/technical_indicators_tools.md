# technical_indicators_tools.py 逻辑说明

## 文件用途
定义 LangChain @tool 装饰的技术指标获取工具 `get_indicators`，供技术分析相关 Agent 调用以获取 13 种技术指标（如 RSI、MACD 等）的分析报告。

## 核心逻辑

### 逗号分隔多指标处理
LLM 在调用工具时可能将多个指标以逗号分隔的形式传入 `indicator` 参数（如 "rsi,macd,bollinger"）。`get_indicators` 会自动拆分、逐个调用供应商接口，并将每个指标的结果拼接返回。这解决了 LLM 不严格遵循"每次只传一个指标"指令的问题。

### 错误容忍
单个指标请求失败（抛出 ValueError）时不会中断整体调用，而是将错误信息作为该指标的结果返回，保证其他指标结果仍然可用。

### 数据路由
与所有工具函数一致，实际数据获取通过 `route_to_vendor("get_indicators", ...)` 委托给数据流层，根据配置路由到具体技术指标供应商。

## 关键函数/类

### get_indicators(symbol, indicator, curr_date, look_back_days=30) -> str
- `symbol: str` — 股票代码，如 AAPL、TSM
- `indicator: str` — 技术指标名称，如 "rsi"、"macd"；支持逗号分隔的多指标输入
- `curr_date: str` — 当前交易日期，YYYY-mm-dd 格式
- `look_back_days: int` — 回看天数，默认 30 天
- 返回格式化的技术指标分析报告字符串，多指标时以双换行分隔
- 内部逻辑：
  1. 将 indicator 按逗号拆分并清理空白，转为小写
  2. 逐个调用 `route_to_vendor("get_indicators", symbol, ind, curr_date, look_back_days)`
  3. 捕获 ValueError 并将错误信息作为该指标结果
  4. 以 "\n\n" 拼接所有结果

## 与其他模块的关系
- **依赖**：
  - `langchain_core.tools.tool` — @tool 装饰器
  - `typing.Annotated` — 参数类型注解
  - `dataflows/interface.route_to_vendor` — 数据供应商路由
- **被依赖**：
  - `utils/agent_utils.py` — 导入 get_indicators 并重新导出
  - 各分析师 Agent 通过 agent_utils 间接使用
