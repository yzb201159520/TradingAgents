# stockstats_utils.py 逻辑说明

## 文件用途
基于 yfinance 和 stockstats 库提供 OHLCV 行情数据加载、缓存管理、技术指标计算和金融报表日期过滤等基础能力，是 yfinance 系列功能的核心支撑模块。

## 核心逻辑
1. **yf_retry()**: 为 yfinance API 调用添加指数退避重试机制。yfinance 在收到 HTTP 429 时抛出 YFRateLimitError 但不内部重试，此包装器对速率限制错误进行最多 max_retries 次重试，退避延迟为 base_delay * 2^attempt 秒。
2. **_clean_dataframe()**: 对行情 DataFrame 进行标准化处理——解析日期列、删除无效行、将价格列转为数值、用前向/后向填充补齐缺失价格，确保数据可被 stockstats 正确消费。
3. **load_ohlcv()**: 获取 OHLCV 数据的核心函数。先通过 safe_ticker_component 校验 symbol 安全性，然后以 5 年为窗口下载数据并缓存为 CSV 文件（按 symbol+日期范围命名）。后续调用直接读缓存。下载完成后调用 _clean_dataframe 清洗，并按 curr_date 过滤以防止回测前视偏差。
4. **filter_financials_by_date()**: 针对 yfinance 财务报表（以财期末日期为列名）过滤掉 curr_date 之后的列，防止使用未来财务数据。
5. **StockstatsUtils.get_stock_stats()**: 加载 OHLCV 数据后用 stockstats 的 wrap 包装，触发指定指标的计算，返回当前日期对应的指标值。非交易日返回 "N/A" 提示。

## 关键函数/类
- **yf_retry(func, max_retries=3, base_delay=2.0)**: 指数退避重试包装器，仅处理 YFRateLimitError，其他异常直接抛出。
- **_clean_dataframe(data)**: 数据清洗——日期解析、无效行删除、数值转换、价格列前向/后向填充。
- **load_ohlcv(symbol, curr_date)**: 获取 OHLCV 数据。含 CSV 缓存（5 年窗口）、安全校验、日期过滤防前视偏差。
- **filter_financials_by_date(data, curr_date)**: 过滤财务报表中超出 curr_date 的列（财期末日期列）。
- **StockstatsUtils**: 静态工具类。
  - **get_stock_stats(symbol, indicator, curr_date)**: 计算指定技术指标并返回当前日期的值。

## 与其他模块的关系
- **依赖**: `.config`（get_config）、`.utils`（safe_ticker_component）、yfinance、stockstats、pandas
- **被依赖**: `dataflows/y_finance.py`（StockstatsUtils、_clean_dataframe、yf_retry、load_ohlcv、filter_financials_by_date）、`dataflows/yfinance_news.py`（yf_retry）
