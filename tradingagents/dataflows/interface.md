# interface.py 逻辑说明

## 文件用途
数据层供应商路由层，根据运行时配置将数据请求分发到 yfinance 或 Alpha Vantage 实现，并提供速率限制自动回退机制。

## 核心逻辑
1. **供应商注册与分类**: 定义 `TOOLS_CATEGORIES` 将数据接口分为四类（核心行情、技术指标、基本面、新闻），定义 `VENDOR_METHODS` 将每个方法名映射到各供应商的具体实现函数。
2. **配置驱动的供应商选择**: `get_vendor()` 先检查方法级配置（`tool_vendors`），再回退到分类级配置（`data_vendors`），支持逗号分隔的多供应商优先级列表。
3. **回退链路由**: `route_to_vendor()` 构建主供应商在前、其余可用供应商在后的回退链，依次尝试调用实现函数。仅当捕获 `AlphaVantageRateLimitError` 时跳到下一个供应商；其他异常直接向上抛出。若所有供应商均不可用，抛出 RuntimeError。
4. **支持多供应商配置**: 供应商配置值可以是逗号分隔的字符串（如 `"alpha_vantage, yfinance"`），实现优先级排序与自动回退。

## 关键函数/类
- **TOOLS_CATEGORIES**: 字典，将工具方法组织为 core_stock_apis / technical_indicators / fundamental_data / news_data 四大分类。
- **VENDOR_LIST**: 列表，注册所有支持的供应商名称。
- **VENDOR_METHODS**: 嵌套字典，格式为 `{方法名: {供应商: 实现函数}}`，覆盖 9 个方法。
- **get_category_for_method(method)**: 在 TOOLS_CATEGORIES 中查找方法所属分类，未找到抛 ValueError。
- **get_vendor(category, method=None)**: 从配置读取供应商，方法级优先于分类级；支持逗号分隔的多供应商。
- **route_to_vendor(method, *args, **kwargs)**: 核心路由。解析供应商优先级列表，构建回退链，依次调用，仅对 AlphaVantageRateLimitError 触发回退。

## 与其他模块的关系
- **依赖**: `.y_finance`（9 个函数）、`.yfinance_news`（2 个函数）、`.alpha_vantage`（8 个函数）、`.alpha_vantage_common`（AlphaVantageRateLimitError）、`.config`（get_config）
- **被依赖**: `agents/utils/core_stock_tools.py`、`agents/utils/technical_indicators_tools.py`、`agents/utils/fundamental_data_tools.py`、`agents/utils/news_data_tools.py`
