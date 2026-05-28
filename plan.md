# TradingAgents A股市场适配方案

## Context

TradingAgents 是一个基于 LangGraph 的多智能体交易分析系统，目前主要支持美股市场。要在国内A股市场跑起来，需要解决三个核心问题：**数据源**（yfinance 对 A 股数据覆盖不完整）、**情绪来源**（StockTwits/Reddit 无 A 股讨论）、**交易规则**（T+1、涨跌停等规则未注入 Agent 提示词）。此外，benchmark_map 缺少 `.SS`/`.SZ` 后缀导致 alpha 计算错误。

**已具备的基础**：CLI 已接受 `.SZ`/`.SH` 后缀，LLM 已支持国内端点（qwen-cn/glm-cn/minimax-cn），vendor routing 系统已支持可插拔后端和 fallback 链。

---

## Phase 1: Benchmark Map + 市场检测（优先级最高，改动最小）

### 1.1 添加 A 股 benchmark 映射
**文件**: `tradingagents/default_config.py` (line 112-121)

在 `benchmark_map` 中添加：
```python
".SS":  "000300.SS",   # 上海 (沪深300)
".SH":  "000300.SS",   # 上海 (Wind/Choice 习惯用 .SH，映射到 .SS)
".SZ":  "399001.SZ",   # 深圳 (深证成指)
```

### 1.2 添加市场检测工具函数
**文件**: `tradingagents/dataflows/utils.py`

新增 `detect_market(ticker) -> str`：
- `.SS`/`.SZ`/`.SH` → `"cn"`
- `-USD`/`-USDT` 等 → `"crypto"`
- 其他 → `"us"`

### 1.3 添加 A 股全球新闻查询词
**文件**: `tradingagents/default_config.py`

新增 `global_news_queries_cn` 配置项，包含央行政策、A股市场、房地产等中文+英文混合查询词。

### 1.4 `.SH` → `.SS` 后缀归一化
**文件**: `tradingagents/dataflows/utils.py`

新增 `normalize_cn_ticker(ticker)` 函数，将 `.SH` 后缀转为 yfinance 兼容的 `.SS`。在 `y_finance.py` 中所有 `yf.Ticker()` 调用前调用此函数。

---

## Phase 2: 市场规则注入 Agent 提示词（中等优先级，中等改动）

### 2.1 扩展 `build_instrument_context()`
**文件**: `tradingagents/agents/utils/agent_utils.py` (line 39-52)

当 `detect_market(ticker) == "cn"` 时，追加 A 股交易规则提示：
- T+1 交易限制
- 涨跌停板制度（主板±10%、创业板/科创板±20%、ST±5%）
- 最低交易单位 100 股
- 交易时间 9:30-11:30, 13:00-15:00
- 无融券做空（大多数投资者）
- 货币单位为人民币

### 2.2 Portfolio Manager 和 Trader 提示词增强
**文件**: `tradingagents/agents/managers/portfolio_manager.py`, `tradingagents/agents/trader/trader.py`

在构建提示词时检测市场，注入 A 股风险提示（T+1 锁仓风险、涨跌停可能套牢、高散户参与度等）。

### 2.3 全球新闻查询自动切换
**文件**: `tradingagents/dataflows/yfinance_news.py`

`get_global_news_yfinance()` 增加 `ticker` 参数，根据 `detect_market(ticker)` 选择 `global_news_queries` 或 `global_news_queries_cn`。对应修改 `news_data_tools.py` 中 `get_global_news` tool 的签名以传递 ticker。

---

## Phase 3: AkShare 数据源接入（核心工作，改动最大）

### 3.1 新增 AkShare 工具模块

| 新文件 | 功能 | 对应 AkShare API |
|--------|------|-----------------|
| `dataflows/akshare_utils.py` | 工具函数：ticker 格式转换、板块检测、重试/缓存 | — |
| `dataflows/akshare_stock.py` | OHLCV 行情数据 | `stock_zh_a_hist()` |
| `dataflows/akshare_fundamentals.py` | 财务报表 | `stock_individual_info_em()`, `stock_balance_sheet_by_report_em()` 等 |
| `dataflows/akshare_news.py` | 新闻 + 龙虎榜 | `stock_news_em()`, `stock_lhb_detail_em()` |

每个函数签名与 yfinance 对应函数兼容，返回格式化的 CSV/文本字符串。

### 3.2 注册 AkShare vendor
**文件**: `tradingagents/dataflows/interface.py`

- `VENDOR_LIST` 添加 `"akshare"`
- `VENDOR_METHODS` 每个方法添加 `"akshare"` 键指向新实现
- `TOOLS_CATEGORIES` 新增 `"ashare_data"` 类别（龙虎榜、融资融券、北向资金等 A 股特有数据）

### 3.3 自动 vendor 切换
**文件**: `tradingagents/graph/trading_graph.py` → `propagate()` 方法

在 `propagate()` 中检测 ticker 市场：
```python
from tradingagents.dataflows.utils import detect_market
market = detect_market(company_name)
if market == "cn":
    self.config["data_vendors"] = {
        "core_stock_apis": "akshare",
        "technical_indicators": "akshare",
        "fundamental_data": "akshare",
        "news_data": "akshare",
    }
set_config(self.config)
```
复用现有 `data_vendors` + `route_to_vendor()` 机制，无需修改 vendor routing 逻辑。

### 3.4 OHLCV 加载支持 AkShare
**文件**: `tradingagents/dataflows/stockstats_utils.py`

修改 `load_ohlcv()`：当 `detect_market(symbol) == "cn"` 时，调用 AkShare 获取 OHLCV 数据而非 yfinance。技术指标计算（stockstats）保持不变，因为只依赖 OHLCV DataFrame。

### 3.5 依赖添加
**文件**: `pyproject.toml`

添加 `akshare` 依赖。

---

## Phase 4: A 股情绪数据源（三个源全部接入）

### 4.1 新增中文情绪数据抓取模块

| 新文件 | 数据源 | 说明 |
|--------|--------|------|
| `dataflows/eastmoney_guba.py` | 东方财富股吧 | 个股讨论帖子，高散户参与度，散户情绪风向标 |
| `dataflows/xueqiu.py` | 雪球 | 投资社区讨论，混合散户/机构，侧重投资逻辑 |
| `dataflows/cls_news.py` | 财联社(CLS) | 实时财经电讯，类似中国版 Reuters，信息最快 |

每个模块遵循 StockTwits/Reddit 的模式：返回格式化文本，失败时返回占位符而非抛异常。

- **股吧**：使用东方财富公开 API 或 AkShare 封装（`ak.stock_guba()`），获取帖子标题、内容摘要、阅读/评论数
- **雪球**：使用雪球公开 API 获取个股讨论帖，提取内容、点赞/回复数
- **财联社**：使用 CLS 电讯 API 获取实时财经快讯，按关键词筛选个股相关新闻

### 4.2 修改 Sentiment Analyst 市场路由
**文件**: `tradingagents/agents/analysts/sentiment_analyst.py`

- `sentiment_analyst_node()` 中根据 `detect_market(ticker)` 选择数据源：
  - `cn` → 东方财富股吧 + 雪球 + 财联社
  - 其他 → StockTwits + Reddit
- `_build_system_message()` 参数化数据源名称和数量（不再硬编码 2 个源），分析指南根据数据源调整：
  - 股吧侧重散户情绪和热度过热信号
  - 雪球侧重投资逻辑和基本面讨论
  - 财联社侧重政策/事件催化剂

---

## 后续可扩展项（本次不实施）

- **Phase 5**: A 股特有数据工具（龙虎榜、融资融券、北向资金）
- **Phase 6**: CLI 改进（更新示例 ticker、添加 TRADINGAGENTS_DATA_VENDOR 环境变量）
- **Tushare Pro**: 可作为 AkShare 的 fallback 或升级选项

---

## 实施顺序与依赖关系

```
Phase 1 (benchmark + detect_market) ← 最先做，改动小，解锁后续
  ↓
Phase 2 (市场规则注入) ← 依赖 detect_market
  ↓
Phase 3 (AkShare 数据源) ← 核心工作，依赖 detect_market + vendor routing
  ↓  (Phase 4 可与 Phase 3 并行)
Phase 4 (三个中文情绪源) ← 依赖 detect_market
```

**最小可用方案**：仅做 Phase 1+2 即可用 yfinance 的有限 A 股数据跑起来（行情数据基本可用，基本面可能不完整）。Phase 3+4 完成后才是真正可用。

---

## 关键文件清单

| 文件 | 改动类型 |
|------|----------|
| `tradingagents/default_config.py` | 修改（benchmark_map, queries, vendors） |
| `tradingagents/dataflows/utils.py` | 修改（新增 detect_market, normalize_cn_ticker） |
| `tradingagents/dataflows/y_finance.py` | 修改（调用 normalize_cn_ticker） |
| `tradingagents/agents/utils/agent_utils.py` | 修改（扩展 build_instrument_context） |
| `tradingagents/agents/analysts/sentiment_analyst.py` | 修改（市场路由） |
| `tradingagents/dataflows/interface.py` | 修改（注册 akshare vendor） |
| `tradingagents/dataflows/stockstats_utils.py` | 修改（load_ohlcv 支持 akshare） |
| `tradingagents/graph/trading_graph.py` | 修改（propagate 中自动切换 vendor） |
| `tradingagents/dataflows/akshare_utils.py` | **新建** |
| `tradingagents/dataflows/akshare_stock.py` | **新建** |
| `tradingagents/dataflows/akshare_fundamentals.py` | **新建** |
| `tradingagents/dataflows/akshare_news.py` | **新建** |
| `tradingagents/dataflows/eastmoney_guba.py` | **新建** |
| `tradingagents/dataflows/xueqiu.py` | **新建** |
| `tradingagents/dataflows/cls_news.py` | **新建** |
| `pyproject.toml` | 修改（添加 akshare 依赖） |

---

## 验证方案

1. **Phase 1 验证**：运行 `ta.propagate("600519.SS", "2025-01-15")`，检查 benchmark 解析为 `000300.SS` 而非 SPY
2. **Phase 2 验证**：检查 Agent 日志/提示词中出现 A 股交易规则文本
3. **Phase 3 验证**：
   - 单独测试各 akshare 函数：`get_stock_akshare("600519", ...)` 返回正确 OHLCV
   - 端到端测试：`ta.propagate("600519.SS", "2025-01-15")` 成功完成全流程
   - 对比 yfinance 和 akshare 对同一 A 股的数据返回质量
4. **Phase 4 验证**：检查 Sentiment Analyst 输出中包含股吧/雪球/财联社数据而非 StockTwits/Reddit
5. **回归测试**：运行 `pytest tests/` 确保美股功能不受影响
