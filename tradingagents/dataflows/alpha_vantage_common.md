# alpha_vantage_common.py 逻辑说明

## 文件用途
提供 Alpha Vantage API 的公共基础设施，包括 API 密钥管理、请求构建与发送、速率限制异常定义和 CSV 数据日期范围过滤，是所有 Alpha Vantage 子模块的底层支撑。

## 核心逻辑
1. **get_api_key()**: 从环境变量 `ALPHA_VANTAGE_API_KEY` 读取 API 密钥，未设置则抛出 ValueError。所有 Alpha Vantage API 请求均依赖此函数。
2. **format_datetime_for_api()**: 将多种日期格式转换为 Alpha Vantage API 要求的 `YYYYMMDDTHHMM` 格式。支持 "YYYY-MM-DD"（时间部分补 0000）和 "YYYY-MM-DD HH:MM" 两种字符串格式，也接受 datetime 对象。
3. **AlphaVantageRateLimitError**: 自定义异常类，用于标识 Alpha Vantage API 速率限制错误。此异常在 interface.py 的路由回退机制中被捕获，触发自动切换到备选供应商（如 yfinance）。
4. **_make_api_request()**: Alpha Vantage API 请求的核心发送函数。流程：组装请求参数（function、apikey、source、entitlement） → 发送 GET 请求 → 检查响应是否为 JSON 格式的错误信息 → 若包含 "rate limit" 或 "api key" 关键字则抛出 AlphaVantageRateLimitError → 否则返回原始响应文本（可能是 JSON 或 CSV）。
5. **_filter_csv_by_date_range()**: 对 Alpha Vantage 返回的 CSV 数据按日期范围过滤。假定首列为时间戳列，解析后过滤到 [start_date, end_date] 范围内。过滤失败时返回原始数据并打印警告。

## 关键函数/类
- **get_api_key()**: 从环境变量获取 Alpha Vantage API 密钥。
- **format_datetime_for_api(date_input)**: 日期格式转换，输出 `YYYYMMDDTHHMM`。
- **AlphaVantageRateLimitError**: 速率限制异常，是供应商自动回退机制的关键信号。
- **_make_api_request(function_name, params)**: 统一 API 请求函数，处理认证、参数组装、速率限制检测。
- **_filter_csv_by_date_range(csv_data, start_date, end_date)**: CSV 数据日期过滤，首列作为时间戳。

## 与其他模块的关系
- **依赖**: requests、pandas、json
- **被依赖**: `dataflows/interface.py`（导入 AlphaVantageRateLimitError 用于回退判断）、`dataflows/alpha_vantage_stock.py`、`dataflows/alpha_vantage_news.py`、`dataflows/alpha_vantage_indicator.py`、`dataflows/alpha_vantage_fundamentals.py`（均通过 alpha_vantage.py 间接使用 _make_api_request、get_api_key、AlphaVantageRateLimitError、format_datetime_for_api）
