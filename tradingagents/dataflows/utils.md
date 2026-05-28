# utils.py 逻辑说明

## 文件用途
为 dataflows 数据层提供通用工具函数，包括安全的 ticker 路径校验、数据输出保存、日期计算和类装饰器。

## 核心逻辑
1. **safe_ticker_component()** 是最重要的安全函数。由于 ticker 来源可能是用户 CLI 输入或 LLM 工具调用（均可被攻击者通过提示注入影响），若不做校验，类似 `"../../../etc/foo"` 的值会在 `os.path.join` 中逃逸出缓存/结果目录。该函数通过正则白名单和纯点号检查，确保值仅包含安全字符且不会造成目录穿越。
2. **save_output()** 提供简单的 DataFrame CSV 保存能力。
3. **get_current_date()** 返回当天日期字符串。
4. **decorate_all_methods()** 是一个类装饰器工厂，可批量为类的所有方法添加指定装饰器。
5. **get_next_weekday()** 将周末日期跳转到下周一，确保日期落在交易日范围内。

## 关键函数/类
- **safe_ticker_component(value, max_len=32)**: 校验 value 是否可安全插入文件系统路径。仅允许字母、数字、点、下划线、短横线、脱字符；拒绝纯点号值和超长值。校验通过原样返回，否则抛出 ValueError。
- **save_output(data, tag, save_path)**: 将 DataFrame 保存为 CSV 文件，并打印保存路径。
- **get_current_date()**: 返回当天日期，格式 "YYYY-MM-DD"。
- **decorate_all_methods(decorator)**: 返回类装饰器，将 decorator 应用于目标类的所有可调用属性。
- **get_next_weekday(date)**: 若 date 为周六/周日，返回下周一；否则原样返回。

## 与其他模块的关系
- **被依赖**: `dataflows/stockstats_utils.py`（safe_ticker_component）、`graph/trading_graph.py`（save_output 等）、`graph/checkpointer.py`、`dataflows/y_finance.py`、`dataflows/yfinance_news.py`
