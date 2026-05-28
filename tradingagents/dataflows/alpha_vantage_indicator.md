# alpha_vantage_indicator.py 逻辑说明

## 文件用途
从 Alpha Vantage API 获取各类技术指标（SMA、EMA、MACD、RSI、布林带、ATR、VWMA）在指定时间窗口内的数值，并返回带有指标解释的格式化文本。

## 核心逻辑
1. **指标验证**：通过 `supported_indicators` 字典校验请求的指标名称是否合法，非法指标直接抛出 `ValueError`。
2. **日期窗口计算**：根据 `curr_date` 和 `look_back_days` 计算回溯起始日期 `before`。
3. **确定 series_type**：每个指标在 `supported_indicators` 中绑定了必需的 `series_type`（如 close），如果指标有硬性要求则覆盖用户传入值。
4. **API 请求**：根据指标类型分发到不同的 Alpha Vantage API 函数：
   - `close_50_sma` / `close_200_sma` → `SMA`
   - `close_10_ema` → `EMA`
   - `macd` / `macds` / `macdh` → `MACD`（三者共用同一 API，通过 CSV 列名区分）
   - `rsi` → `RSI`
   - `boll` / `boll_ub` / `boll_lb` → `BBANDS`（共用同一 API，通过列名区分上/中/下轨）
   - `atr` → `ATR`
   - `vwma` → Alpha Vantage 无直接接口，返回说明文本
5. **CSV 解析与日期过滤**：解析返回的 CSV 数据，通过 `col_name_map` 将内部指标名映射到 Alpha Vantage CSV 列名，筛选日期在 `[before, curr_date]` 范围内的行。
6. **输出格式化**：按日期排序后，拼接为 "日期: 数值" 格式的文本，末尾附上 `indicator_descriptions` 中对应的指标说明（含用法建议和注意事项）。

## 关键函数/类
- **`get_indicator(symbol, indicator, curr_date, look_back_days, interval, time_period, series_type) -> str`**
  - `symbol`：股票代码
  - `indicator`：技术指标名称，必须在 `supported_indicators` 中
  - `curr_date`：当前交易日，格式 yyyy-mm-dd
  - `look_back_days`：回溯天数
  - `interval`：时间间隔，默认 "daily"
  - `time_period`：计算周期，默认 14
  - `series_type`：价格类型，默认 "close"
  - 返回值：包含指标数值序列和解释说明的格式化字符串

- **`supported_indicators`**：字典，键为内部指标名，值为 `(API显示名, 必需series_type)` 元组
- **`indicator_descriptions`**：字典，键为内部指标名，值为指标的解释文本（含用法和提示）

## 与其他模块的关系
- **依赖**：`alpha_vantage_common._make_api_request` — 发起 API 请求
- **被依赖**：`alpha_vantage.py` — 通过门面模块再导出；`interface.py` — 注册为 `get_indicators` 的 Alpha Vantage 实现
