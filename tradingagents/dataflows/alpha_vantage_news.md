# alpha_vantage_news.py 逻辑说明

## 文件用途
从 Alpha Vantage API 获取新闻情绪数据和内幕交易数据，支持按股票代码筛选新闻、获取全球宏观新闻、以及查询公司内部人交易记录。

## 核心逻辑
1. **个股新闻（get_news）**：
   - 接收 `ticker`、`start_date`、`end_date` 三个参数。
   - 调用 `format_datetime_for_api` 将日期转换为 Alpha Vantage 要求的 `YYYYMMDDTHHMM` 格式。
   - 调用 `NEWS_SENTIMENT` 接口，以 `tickers` 参数过滤与指定股票相关的新闻，返回含情绪评分的 JSON 数据。

2. **全球宏观新闻（get_global_news）**：
   - 接收 `curr_date`、`look_back_days`、`limit` 三个参数。
   - 根据 `curr_date` 和 `look_back_days` 计算起始日期。
   - 调用 `NEWS_SENTIMENT` 接口，但不限定股票代码，而是以 `topics` 参数过滤主题（financial_markets、economy_macro、economy_monetary），获取全球宏观金融新闻。
   - `limit` 参数控制返回的最大文章数量。

3. **内幕交易（get_insider_transactions）**：
   - 接收 `symbol` 参数。
   - 调用 `INSIDER_TRANSACTIONS` 接口，获取公司创始人、高管、董事会成员等的最新及历史交易记录。

## 关键函数/类
- **`get_news(ticker, start_date, end_date) -> dict | str`**
  - `ticker`：股票代码
  - `start_date` / `end_date`：日期范围
  - 返回与指定股票相关的新闻情绪数据

- **`get_global_news(curr_date, look_back_days, limit) -> dict | str`**
  - `curr_date`：当前日期，格式 yyyy-mm-dd
  - `look_back_days`：回溯天数，默认 7
  - `limit`：最大文章数，默认 50
  - 返回全球宏观金融新闻情绪数据

- **`get_insider_transactions(symbol) -> dict | str`**
  - `symbol`：股票代码
  - 返回公司内部人交易记录

## 与其他模块的关系
- **依赖**：`alpha_vantage_common._make_api_request` — 发起 API 请求；`alpha_vantage_common.format_datetime_for_api` — 日期格式转换
- **被依赖**：`alpha_vantage.py` — 通过门面模块再导出三个函数；`interface.py` — 注册为新闻数据类别的 Alpha Vantage 实现
