# yfinance_news.py 逻辑说明

## 文件用途
封装 Yahoo Finance 新闻数据获取功能，提供个股新闻和全球宏观经济新闻两种查询能力。

## 核心逻辑
1. **_extract_article_data()**: 处理 yfinance 新闻数据两种结构——嵌套 content 结构（新版 API）和平铺结构（旧版/兼容格式）。从嵌套结构中提取标题、摘要、发布者、URL（优先 canonicalUrl 其次 clickThroughUrl）和发布时间；平铺结构直接读取顶级字段。
2. **get_news_yfinance()**: 获取指定 ticker 的个股新闻。流程：通过 yf.Ticker 获取新闻列表 → 逐篇提取数据 → 按发布时间过滤（仅保留 start_date 到 end_date+1 天范围内的文章）→ 格式化为 Markdown 标题+摘要+链接。文章数量由配置项 news_article_limit 控制。
3. **get_global_news_yfinance()**: 获取全球/宏观经济新闻。流程：按配置中的多个搜索关键词（global_news_queries）逐个执行 yf.Search → 去重（按标题） → 按发布时间过滤（排除 curr_date 之后的文章，防止前视偏差）→ 格式化输出。回溯天数和文章上限分别由 global_news_lookback_days 和 global_news_article_limit 控制。

两个函数均通过 yf_retry 包装 yfinance 调用以处理速率限制，异常时返回错误信息字符串而非抛出异常。

## 关键函数/类
- **_extract_article_data(article)**: 从 yfinance 新闻原始数据中提取结构化字段，兼容嵌套 content 和平铺两种格式。返回字典包含 title、summary、publisher、link、pub_date。
- **get_news_yfinance(ticker, start_date, end_date)**: 获取个股新闻。按日期范围过滤，返回 Markdown 格式字符串。
- **get_global_news_yfinance(curr_date, look_back_days, limit)**: 获取全球新闻。支持多关键词搜索、标题去重、未来日期过滤，返回 Markdown 格式字符串。

## 与其他模块的关系
- **依赖**: `.config`（get_config）、`.stockstats_utils`（yf_retry）、yfinance、dateutil
- **被依赖**: `dataflows/interface.py`（get_news_yfinance 和 get_global_news_yfinance 被 VENDOR_METHODS 映射注册）
