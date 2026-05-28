# alpha_vantage_stock.py 逻辑说明

## 文件用途
从 Alpha Vantage API 获取股票每日 OHLCV（开盘/最高/最低/收盘/成交量）及调整后收盘价、拆股/分红事件数据，并按指定日期范围过滤。

## 核心逻辑
1. 解析 `start_date`，计算其距今天的天数。
2. 若起始日期距今不足 100 天，使用 `outputsize=compact`（仅返回最近 100 个交易日数据）；否则使用 `outputsize=full`（返回完整历史），以在数据完整性与 API 响应体量之间取得平衡。
3. 调用 `_make_api_request("TIME_SERIES_DAILY_ADJUSTED", params)` 获取 CSV 格式的原始数据。
4. 调用 `_filter_csv_by_date_range` 对返回的 CSV 按日期区间 `[start_date, end_date]` 进行过滤，使用 pandas 进行解析和筛选，最终返回过滤后的 CSV 字符串。

## 关键函数/类
- **`get_stock(symbol, start_date, end_date) -> str`**
  - `symbol`：股票代码，如 "IBM"
  - `start_date`：起始日期，格式 yyyy-mm-dd
  - `end_date`：结束日期，格式 yyyy-mm-dd
  - 返回值：经日期过滤后的 CSV 字符串，包含每日调整后时间序列数据

## 与其他模块的关系
- **依赖**：`alpha_vantage_common._make_api_request` — 发起 API 请求；`alpha_vantage_common._filter_csv_by_date_range` — CSV 日期过滤
- **被依赖**：`alpha_vantage.py` — 通过门面模块再导出；`interface.py` — 注册为 `get_stock_data` 的 Alpha Vantage 实现
