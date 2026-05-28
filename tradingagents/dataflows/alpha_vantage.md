# alpha_vantage.py 逻辑说明

## 文件用途
Alpha Vantage 数据源的统一门面模块，将子模块的函数汇聚到同一命名空间下供上层调用。

## 核心逻辑
该文件本身不包含任何处理逻辑，仅做导入再导出（re-export）。它从四个专职子模块中导入所有公开函数：

- `alpha_vantage_stock.get_stock` — 股票价格数据
- `alpha_vantage_indicator.get_indicator` — 技术指标
- `alpha_vantage_fundamentals` 中的 `get_fundamentals`、`get_balance_sheet`、`get_cashflow`、`get_income_statement` — 基本面数据
- `alpha_vantage_news` 中的 `get_news`、`get_global_news`、`get_insider_transactions` — 新闻与内幕交易

上层 `interface.py` 通过 `from .alpha_vantage import ...` 一次性获取所有 Alpha Vantage 实现，并将其注册到 `VENDOR_METHODS` 路由表中，从而支持按配置切换数据供应商（yfinance / alpha_vantage）并实现速率限制时的自动回退。

## 关键函数/类
无自定义函数/类。所有符号均从子模块直接导入：
- `get_stock` — 委托至 `alpha_vantage_stock`
- `get_indicator` — 委托至 `alpha_vantage_indicator`
- `get_fundamentals`、`get_balance_sheet`、`get_cashflow`、`get_income_statement` — 委托至 `alpha_vantage_fundamentals`
- `get_news`、`get_global_news`、`get_insider_transactions` — 委托至 `alpha_vantage_news`

## 与其他模块的关系
- **依赖**：`alpha_vantage_stock`、`alpha_vantage_indicator`、`alpha_vantage_fundamentals`、`alpha_vantage_news`
- **被依赖**：`dataflows/interface.py` — 通过此门面模块导入 Alpha Vantage 全部实现并注册到供应商路由表
