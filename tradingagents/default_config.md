# default_config.py 逻辑说明

## 文件用途
定义 TradingAgents 系统的全局默认配置字典 `DEFAULT_CONFIG`，并提供环境变量到配置键的自动映射与类型强制转换机制，是整个系统配置的"单一事实来源"。

## 核心逻辑

### 环境变量覆盖机制
文件维护了一个 `_ENV_OVERRIDES` 映射表，将 `TRADINGAGENTS_*` 前缀的环境变量名映射到配置字典中的键名。用户只需在 `.env` 中设置对应环境变量，即可覆盖默认值，无需修改代码或入口脚本。

### 类型强制转换
`_coerce()` 函数根据配置字典中已有默认值的类型，自动将环境变量的字符串值转换为正确类型：
- 布尔值：将 `"true"`、`"1"`、`"yes"`、`"on"` 视为 `True`，其余为 `False`
- 整数：调用 `int()` 转换
- 浮点数：调用 `float()` 转换
- 字符串：原样保留

### 配置构建流程
`DEFAULT_CONFIG` 的生成分为两步：
1. 定义包含所有默认值的字典字面量
2. 调用 `_apply_env_overrides()` 就地用环境变量覆盖对应键值

### 配置项概览
| 类别 | 主要键 | 说明 |
|------|--------|------|
| 路径 | `project_dir`、`results_dir`、`data_cache_dir`、`memory_log_path` | 项目目录、日志、缓存、记忆文件路径 |
| LLM | `llm_provider`、`deep_think_llm`、`quick_think_llm`、`backend_url` | LLM 提供商与模型选择 |
| 思考级别 | `google_thinking_level`、`openai_reasoning_effort`、`anthropic_effort` | 各提供商推理力度配置 |
| 检查点 | `checkpoint_enabled` | LangGraph 断点续跑开关 |
| 输出 | `output_language` | 报告与决策输出语言 |
| 辩论轮次 | `max_debate_rounds`、`max_risk_discuss_rounds` | 研究/风险辩论最大轮数 |
| 新闻参数 | `news_article_limit`、`global_news_article_limit`、`global_news_lookback_days`、`global_news_queries` | 新闻获取数量与范围 |
| 数据供应商 | `data_vendors`（分类级）、`tool_vendors`（工具级） | 数据接口选择，工具级优先于分类级 |
| 基准 | `benchmark_ticker`、`benchmark_map` | Alpha 计算的基准标的与交易所后缀映射 |

## 关键函数/类

### `_coerce(value: str, reference) -> bool | int | float | str`
将环境变量字符串值按 `reference` 的类型强制转换。

### `_apply_env_overrides(config: dict) -> dict`
遍历 `_ENV_OVERRIDES`，将非空环境变量值经 `_coerce()` 转换后写入 `config` 字典（就地修改并返回）。

### `DEFAULT_CONFIG: dict`
系统默认配置常量，由内置默认值 + 环境变量覆盖后生成。

## 与其他模块的关系
- **依赖**：`os`（标准库）；`tradingagents.__init__`（确保 `.env` 在此模块加载前已读入环境）
- **被依赖**：
  - `tradingagents.dataflows.config`：直接 `import` 并深拷贝 `DEFAULT_CONFIG` 作为运行时配置的初始值
  - `tradingagents.graph.trading_graph`：直接导入 `DEFAULT_CONFIG` 作为回退配置
  - `tests/test_env_overrides.py`、`tests/test_dataflows_config.py`：单元测试
