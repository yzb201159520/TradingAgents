# cli/utils.py 逻辑说明

## 文件用途
CLI 交互式工具函数集，提供股票代码输入、资产类型检测、分析师选择、研究深度选择、LLM 提供商/模型选择、区域端点选择、API Key 确保和输出语言选择等用户交互功能。

## 核心逻辑

### 股票代码处理
- `get_ticker()`：使用 questionary 文本输入获取股票代码，自动标准化为大写并保留交易所后缀（如 .TO、.T、.HK）
- `normalize_ticker_symbol(ticker)`：去除首尾空格并转大写
- `detect_asset_type(ticker)`：根据后缀（-USD、-USDT、-USDC、-BTC、-ETH）自动检测为加密货币或股票
- `filter_analysts_for_asset_type(analysts, asset_type)`：加密货币资产过滤掉基本面分析师

### 分析参数选择
- `get_analysis_date()`：交互式输入 YYYY-MM-DD 格式日期，含正则验证和日期合法性检查
- `select_analysts(asset_type)`：交互式多选框选择分析师团队，按资产类型过滤可选项
- `select_research_depth()`：交互式单选研究深度（Shallow=1 / Medium=3 / Deep=5）

### LLM 提供商与模型选择
- `select_llm_provider()`：交互式选择 11 家 LLM 提供商，返回 (provider_key, base_url) 元组
  - 内置提供商列表：OpenAI、Google、Anthropic、xAI、DeepSeek、Qwen、GLM、MiniMax、OpenRouter、Azure OpenAI、Ollama
  - Ollama 支持 `OLLAMA_BASE_URL` 环境变量自定义端点
- `select_shallow_thinking_agent(provider)` / `select_deep_thinking_agent(provider)`：分别选择浅层和深层思考模型
- `_select_model(provider, mode)`：统一模型选择逻辑，按提供商分派：
  - OpenRouter：从 API 获取最新模型列表，支持自定义模型 ID
  - Azure：输入部署名称
  - 其他：从 `get_model_options()` 获取模型列表，支持自定义 ID
- `_fetch_openrouter_models()`：从 OpenRouter API 获取可用模型列表

### 区域端点选择
部分提供商在不同地区有独立端点，API Key 不通用：
- `ask_qwen_region()`：国际站 vs 中国站
- `ask_minimax_region()`：全球站 vs 中国站
- `ask_glm_region()`：Z.AI 国际站 vs BigModel 中国站

### 提供商特定配置
- `ask_openai_reasoning_effort()`：OpenAI 推理努力级别（Low/Medium/High）
- `ask_anthropic_effort()`：Anthropic effort 级别（Low/Medium/High）
- `ask_gemini_thinking_config()`：Gemini 思考模式（Enable Thinking / Minimal）
- `confirm_ollama_endpoint(url)`：确认 Ollama 端点，含缺失 scheme/端口的软警告

### API Key 管理
- `ensure_api_key(provider)`：确保提供商的 API Key 存在于环境中
  - 已存在则直接返回
  - 不存在则交互式提示用户粘贴，使用 python-dotenv 持久化到 `.env` 文件
  - Ollama 等不需要 Key 的提供商返回 None

### 输出语言
- `ask_output_language()`：交互式选择报告输出语言（11 种预设 + 自定义输入）

### 常量定义
- `TICKER_INPUT_EXAMPLES`：股票代码输入示例提示
- `ANALYST_ORDER`：分析师显示顺序和枚举映射
- `CRYPTO_SUFFIXES`：加密货币代码后缀列表

## 关键函数/类

- `get_ticker() -> str`：获取股票代码输入
- `normalize_ticker_symbol(ticker) -> str`：标准化股票代码
- `detect_asset_type(ticker) -> AssetType`：检测资产类型
- `filter_analysts_for_asset_type(analysts, asset_type) -> List[AnalystType]`：按资产类型过滤分析师
- `get_analysis_date() -> str`：获取分析日期
- `select_analysts(asset_type) -> List[AnalystType]`：选择分析师团队
- `select_research_depth() -> int`：选择研究深度（1/3/5）
- `select_llm_provider() -> tuple[str, str | None]`：选择 LLM 提供商和端点
- `select_shallow_thinking_agent(provider) -> str`：选择浅层思考模型
- `select_deep_thinking_agent(provider) -> str`：选择深层思考模型
- `ask_qwen_region() -> tuple[str, str]`：选择 Qwen 区域
- `ask_minimax_region() -> tuple[str, str]`：选择 MiniMax 区域
- `ask_glm_region() -> tuple[str, str]`：选择 GLM 区域
- `ask_openai_reasoning_effort() -> str`：选择 OpenAI 推理努力级别
- `ask_anthropic_effort() -> str | None`：选择 Anthropic effort 级别
- `ask_gemini_thinking_config() -> str | None`：选择 Gemini 思考模式
- `confirm_ollama_endpoint(url) -> None`：确认 Ollama 端点
- `ensure_api_key(provider) -> Optional[str]`：确保 API Key 可用
- `ask_output_language() -> str`：选择输出语言

## 与其他模块的关系
- **依赖**：
  - `cli.models.AnalystType` / `AssetType`：分析师和资产类型枚举
  - `tradingagents.llm_clients.api_key_env.get_api_key_env`：获取提供商对应的 API Key 环境变量名
  - `tradingagents.llm_clients.model_catalog.get_model_options`：获取提供商的模型选项列表
  - `questionary`：交互式问答库
  - `rich.console.Console`：Rich 终端输出
  - `dotenv`：.env 文件读写
- **被依赖**：
  - `cli/main.py`：`from cli.utils import *` 导入所有公开函数，在 `get_user_selections()` 中逐步调用
