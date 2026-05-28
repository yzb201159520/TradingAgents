# test.py 逻辑说明

## 文件用途
快速数据流测试脚本，用于验证优化后的 yfinance 数据获取接口的性能和正确性。

## 核心逻辑
1. 导入 `tradingagents.dataflows.y_finance` 中的多个数据获取函数（`get_YFin_data_online`、`get_stock_stats_indicators_window`、`get_balance_sheet`、`get_cashflow`、`get_income_statement`、`get_insider_transactions`）。
2. 以 "AAPL" 为股票代码、"macd" 为指标类型、"2024-11-01" 为截止日期、30 天为回看窗口，调用 `get_stock_stats_indicators_window` 获取技术指标数据。
3. 测量执行时间并打印耗时、结果字符长度和内容。
4. 该脚本主要用于开发阶段快速验证数据流接口的性能优化效果（30 天回看窗口的优化实现）。

## 关键函数/类
- 无自定义函数/类，整个文件为顶层测试脚本。

## 与其他模块的关系
- **依赖**：
  - `tradingagents.dataflows.y_finance`：yfinance 数据流模块，提供股票数据获取函数
    - `get_stock_stats_indicators_window`：获取指定窗口内的技术指标数据
    - `get_YFin_data_online`：在线获取 Yahoo Finance 数据
    - `get_balance_sheet` / `get_cashflow` / `get_income_statement` / `get_insider_transactions`：财务报表和内部交易数据（已导入但本脚本未使用）
- **被依赖**：无（独立测试脚本）
