# model_catalog.py 逻辑说明

## 文件用途
为 CLI 下拉菜单提供共享的模型目录数据，同时作为模型名称验证的数据源。定义了每个提供商在"快速思考"（quick）和"深度思考"（deep）两种模式下可选的模型列表。

## 核心逻辑

### 数据结构
- `ModelOption = Tuple[str, str]`：模型选项，元组格式为 `(显示标签, 模型ID)`
- `ProviderModeOptions = Dict[str, Dict[str, List[ModelOption]]]`：提供商 -> 模式 -> 选项列表的嵌套字典

### 双区域提供商共享模型列表
Qwen（国际/中国）、GLM（国际/中国）、MiniMax（国际/中国）各自的国际站和中国站使用相同的模型 ID，因此共享同一份模型列表（`_QWEN_MODELS`、`_GLM_MODELS`、`_MINIMAX_MODELS`），只是 base_url 不同。

### 模型目录 MODEL_OPTIONS
按提供商和模式（quick/deep）组织，覆盖 12 个提供商：
- **openai**：GPT-5.5/5.4/5.2/4.1 系列
- **anthropic**：Claude Opus/Sonnet/Haiku 4.5+ 系列
- **google**：Gemini 3/2.5 Flash/Pro 系列
- **xai**：Grok 4/4.20 系列
- **deepseek**：V4 Pro/Flash、V3.2 系列
- **qwen/qwen-cn**：Qwen 3.6/3.5 Plus/Flash 系列
- **glm/glm-cn**：GLM-5/5.1/4.7/4.5-Air 系列
- **minimax/minimax-cn**：MiniMax-M2.7/M2.5/M2.1/M2 系列
- **ollama**：Qwen3、GPT-OSS、GLM-4.7-Flash 本地模型

### 设计决策
1. 仅暴露版本化 ID（如 `qwen3.6-flash`），不暴露无版本别名（如 `qwen-plus`），因为阿里云的别名会自动升级底座模型导致行为漂移；用户若想用别名可通过 "Custom model ID" 手动输入。
2. 每个提供商列表末尾提供 "Custom model ID" 选项，允许用户输入目录外的任意模型 ID。
3. OpenRouter 的模型目录通过 API 动态获取，Azure 接受任何已部署模型名，因此两者不在静态目录中。
4. Ollama 的显示标签不标注"本地"，因为端点可通过 `OLLAMA_BASE_URL` 环境变量指向远程主机。

### get_known_models 函数
从 MODEL_OPTIONS 中提取所有提供商的已知模型 ID 列表（去重排序），供 validators 模块使用。排除 "custom" 占位符。

## 关键函数/类
- `MODEL_OPTIONS: ProviderModeOptions`：完整的模型目录数据
- `get_model_options(provider, mode) -> List[ModelOption]`：返回指定提供商和模式下的模型选项列表
- `get_known_models() -> Dict[str, List[str]]`：构建所有提供商的已知模型名列表（去重排序）

## 与其他模块的关系
- 依赖：无外部模块依赖
- 被依赖：`validators.py`（`get_known_models()` 提供验证数据源）、CLI 的模型选择界面（`get_model_options()` 提供下拉菜单选项）
