# y_finance.py 逻辑说明

## 文件用途
封装 Yahoo Finance API，提供股票行情查询、技术指标窗口计算、基本面数据获取、三大财务报表（资产负债表/现金流量/利润表）和内部人交易数据的获取功能。

## 核心逻辑
1. **get_YFin_data_online()**: 通过 yfinance 获取指定日期范围的股票 OHLCV 数据，去除时区信息、数值保留两位小数后以 CSV 字符串形式返回，附带元信息头部。
2. **get_stock_stats_indicators_window()**: 核心技术指标计算函数。先从 `best_ind_params` 字典校验指标是否受支持（支持 14 种指标：SMA、EMA、MACD、RSI、Bollinger Bands、ATR、VWMA、MFI 等），然后调用 `_get_stock_stats_bulk()` 批量计算指定回溯窗口内所有日期的指标值。若批量计算失败，回退到逐日调用 `get_stockstats_indicator()` 的方式。结果附带指标说明文本。
3. **_get_stock_stats_bulk()**: 批量计算优化函数。一次性加载 OHLCV 数据并触发 stockstats 指标计算，将所有日期的指标值构建为字典返回，避免重复加载。
4. **get_stockstats_indicator()**: 单日指标计算（兼容旧逻辑），委托给 StockstatsUtils.get_stock_stats()。
5. **get_fundamentals()**: 获取公司基本面概览，从 yfinance Ticker.info 提取 28 个关键字段（名称、行业、市值、PE、EPS、股息率、Beta 等），格式化为文本输出。
6. **get_balance_sheet() / get_cashflow() / get_income_statement()**: 三大财务报表获取函数，支持 annual/quarterly 频率选择，均通过 filter_financials_by_date 过滤未来数据，以 CSV 字符串返回。
7. **get_insider_transactions()**: 获取内部人交易数据，以 CSV 字符串返回。

所有函数均通过 yf_retry 包装 yfinance 调用以处理速率限制。

## 关键函数/类
- **get_YFin_data_online(symbol, start_date, end_date)**: 获取股票历史行情，返回含元信息的 CSV 字符串。
- **get_stock_stats_indicators_window(symbol, indicator, curr_date, look_back_days)**: 计算技术指标在回溯窗口内逐日的值，返回日期-指标值列表及指标说明。支持 14 种指标。
- **_get_stock_stats_bulk(symbol, indicator, curr_date)**: 批量计算所有日期的指标值，返回字典 `{日期: 指标值}`。
- **get_stockstats_indicator(symbol, indicator, curr_date)**: 单日指标值计算（回退用）。
- **get_fundamentals(ticker, curr_date)**: 公司基本面概览，28 个关键字段。
- **get_balance_sheet(ticker, freq, curr_date)**: 资产负债表，支持年度/季度。
- **get_cashflow(ticker, freq, curr_date)**: 现金流量表。
- **get_income_statement(ticker, freq, curr_date)**: 利润表。
- **get_insider_transactions(ticker)**: 内部人交易数据。

## 与其他模块的关系
- **依赖**: `.stockstats_utils`（StockstatsUtils、_clean_dataframe、yf_retry、load_ohlcv、filter_financials_by_date）、yfinance、stockstats、pandas
- **被依赖**: `dataflows/interface.py`（9 个函数被 VENDOR_METHODS 映射注册）
