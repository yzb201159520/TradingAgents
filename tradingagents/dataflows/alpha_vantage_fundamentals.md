# alpha_vantage_fundamentals.py 逻辑说明

## 文件用途
从 Alpha Vantage API 获取公司基本面数据，包括公司概览（财务比率与关键指标）、资产负债表、现金流量表和利润表，并提供前视偏差（look-ahead bias）防护。

## 核心逻辑
1. **公司概览**：`get_fundamentals` 调用 Alpha Vantage 的 `OVERVIEW` 接口，返回包含市盈率、市值、股息率等综合基本面指标的 JSON 数据。该接口不支持日期过滤，因此 `curr_date` 参数虽被接受但未使用。

2. **财务报表获取**：`get_balance_sheet`、`get_cashflow`、`get_income_statement` 分别调用 `BALANCE_SHEET`、`CASH_FLOW`、`INCOME_STATEMENT` 接口，获取季度/年度财务报表数据。

3. **前视偏差防护**：所有财务报表函数在返回结果前调用 `_filter_reports_by_date`，将 `annualReports` 和 `quarterlyReports` 中 `fiscalDateEnding` 晚于 `curr_date` 的条目移除。这确保在回测/模拟场景下，系统只能看到当前交易日之前已经公布的财报数据，避免利用未来信息做决策。

## 关键函数/类
- **`_filter_reports_by_date(result, curr_date) -> dict`**
  - `result`：Alpha Vantage 返回的原始 JSON 字典
  - `curr_date`：当前模拟日期，格式 yyyy-mm-dd
  - 过滤 `annualReports` 和 `quarterlyReports` 中 `fiscalDateEnding > curr_date` 的条目

- **`get_fundamentals(ticker, curr_date) -> str`**
  - `ticker`：股票代码
  - `curr_date`：当前日期（未使用，保留接口一致性）
  - 返回公司概览 JSON 字符串

- **`get_balance_sheet(ticker, freq, curr_date)`**
  - `freq`：频率（quarterly/annual），保留参数但 Alpha Vantage 不区分
  - 返回经日期过滤的资产负债表数据

- **`get_cashflow(ticker, freq, curr_date)`**
  - 返回经日期过滤的现金流量表数据

- **`get_income_statement(ticker, freq, curr_date)`**
  - 返回经日期过滤的利润表数据

## 与其他模块的关系
- **依赖**：`alpha_vantage_common._make_api_request` — 发起 API 请求
- **被依赖**：`alpha_vantage.py` — 通过门面模块再导出四个函数；`interface.py` — 注册为基本面数据类别的 Alpha Vantage 实现
