# anthropic_client.py 逻辑说明

## 文件用途
处理 Anthropic (Claude) 系列模型的客户端实现，包括内容归一化、effort 参数门控和模型验证。

## 核心逻辑

### NormalizedChatAnthropic
重写 `invoke()` 方法，调用 `normalize_content()` 将 Claude 返回的类型化内容块（extended thinking、tool use 等产生的列表）归一化为纯字符串，确保下游 Agent 处理一致。

### effort 参数门控
Anthropic 的 `effort` 参数（控制推理深度）仅被 Opus 4.5+ 和 Sonnet 4.5+ 接受。Haiku 系列（任何已发布版本）传入此参数会返回 400 错误（#831）。

门控逻辑：
1. `_EFFORT_EXACT`：精确匹配集合，包含特殊预览名称（如 `claude-mythos-preview`）
2. `_EFFORT_PATTERN`：正则 `^claude-(opus|sonnet)-\d+-\d+$`，匹配未来 Opus/Sonnet 版本号格式
3. `_supports_effort(model)`：先检查精确匹配，再检查模式匹配；Haiku 及其他不符合的模型返回 False

### AnthropicClient
1. `get_llm()` 方法：
   - 调用 `warn_if_unknown_model()` 检查模型
   - 透传 `timeout`、`max_retries`、`api_key`、`max_tokens`、`callbacks`、`http_client`、`http_async_client`、`effort` 等参数
   - 对 `effort` 参数进行门控：若模型不支持则跳过，避免 API 400 错误
   - 返回 `NormalizedChatAnthropic` 实例
2. 构造函数支持可选 `base_url`，用于自定义 API 端点（如企业代理）。

## 关键函数/类
- `NormalizedChatAnthropic(ChatAnthropic)`：内容归一化的 Anthropic 聊天模型
  - `invoke()`：归一化 content
- `AnthropicClient(BaseLLMClient)`：Anthropic 客户端
  - `__init__(model, base_url, **kwargs)`：初始化
  - `get_llm() -> Any`：返回配置好的 ChatAnthropic 实例
  - `validate_model() -> bool`：通过 validators 模块验证模型
- `_supports_effort(model) -> bool`：判断模型是否支持 effort 参数

## 与其他模块的关系
- 依赖：`base_client.BaseLLMClient/normalize_content`、`validators.validate_model`、`langchain_anthropic.ChatAnthropic`
- 被依赖：`factory.py`（当 provider == "anthropic" 时创建）
