# openai_client.py 逻辑说明

## 文件用途
处理 OpenAI 原生及所有 OpenAI 兼容提供商（xAI、DeepSeek、Qwen、GLM、MiniMax、Ollama、OpenRouter）的客户端实现，是 LLM 客户端层中最复杂、覆盖提供商最多的模块。

## 核心逻辑

### 类继承体系
`ChatOpenAI` -> `NormalizedChatOpenAI` -> `DeepSeekChatOpenAI` / `MinimaxChatOpenAI`，通过子类化将提供商特有逻辑隔离，保持基类简洁。

### NormalizedChatOpenAI
1. 重写 `invoke()` 方法，调用 `normalize_content()` 将响应 content 从类型化块列表归一化为纯字符串。
2. 重写 `with_structured_output()` 方法，查询能力表（`get_capabilities`）决定结构化输出的实现方式：
   - 若 `preferred_structured_method == "none"`，抛出 `NotImplementedError`，让 Agent 工厂回退到自由文本生成
   - 否则使用能力表推荐的 method
   - 对于 `function_calling` 方式但不支持 `tool_choice` 的模型（如 DeepSeek V4/reasoner），将 `tool_choice` 设为 `None` 以避免 API 400 错误

### DeepSeekChatOpenAI
实现 DeepSeek 思维模式的推理内容往返（round-trip）：
1. `_get_request_payload()`：在发出请求时，遍历消息历史，将 `AIMessage` 中的 `reasoning_content` 附加到请求载荷中。DeepSeek 思维模型要求在后续请求中回传上一轮的推理内容，否则 API 返回 400。
2. `_create_chat_result()`：在收到响应时，从原始响应中提取 `reasoning_content` 并存入 `AIMessage.additional_kwargs`，供下一轮请求使用。

### MinimaxChatOpenAI
实现 MiniMax M2.x 推理模型的 `reasoning_split` 处理：
1. `_get_request_payload()`：查询能力表，若模型需要 `reasoning_split`，在请求载荷中设置 `reasoning_split=True`。这使 M2.x 的思维块被重定向到 `reasoning_details` 字段，避免污染 `content`。非推理模型（如 MiniMax-Text-01）不接受此参数，因此通过能力标志进行门控。

### OpenAIClient
1. 构造函数接收 `provider` 参数（默认 "openai"），存储为实例属性。
2. `get_llm()` 方法：
   - 调用 `warn_if_unknown_model()` 检查模型
   - 根据提供商选择合适的 ChatOpenAI 子类（DeepSeek -> `DeepSeekChatOpenAI`，MiniMax -> `MinimaxChatOpenAI`，其他 -> `NormalizedChatOpenAI`）
   - 对于 `_PROVIDER_BASE_URL` 中的提供商，自动设置 `base_url`（支持环境变量覆盖，目前仅 Ollama 的 `OLLAMA_BASE_URL`）和从环境变量读取 API 密钥
   - 通过 `get_api_key_env()` 查询密钥环境变量名，若未设置则抛出 `ValueError`
   - Ollama 无密钥要求，使用占位字符串 "ollama"
   - 原生 OpenAI 启用 Responses API（`use_responses_api=True`），支持所有模型家族的 `reasoning_effort` 与函数工具
   - 透传 `timeout`、`max_retries`、`reasoning_effort`、`api_key`、`callbacks`、`http_client`、`http_async_client` 等参数

### 双区域提供商
Qwen（国际/中国）、GLM（国际/中国）、MiniMax（国际/中国）各自维护独立的 base_url，因为国际站和中国站账号不互通（#758）。

### _input_to_messages 辅助函数
将 LangChain 的多种输入格式（消息列表、ChatPromptValue、其他）统一转为消息对象列表，供 DeepSeek 思维内容往返逻辑使用。

## 关键函数/类
- `NormalizedChatOpenAI(ChatOpenAI)`：内容归一化 + 能力感知的结构化输出绑定
  - `invoke()`：归一化 content
  - `with_structured_output()`：根据能力表选择方法和参数
- `DeepSeekChatOpenAI(NormalizedChatOpenAI)`：DeepSeek 推理内容往返
  - `_get_request_payload()`：发送时回传 reasoning_content
  - `_create_chat_result()`：接收时提取 reasoning_content
- `MinimaxChatOpenAI(NormalizedChatOpenAI)`：MiniMax reasoning_split 处理
  - `_get_request_payload()`：注入 reasoning_split=True
- `OpenAIClient(BaseLLMClient)`：OpenAI 及兼容提供商的客户端
  - `__init__(model, base_url, provider, **kwargs)`：初始化，provider 区分具体提供商
  - `get_llm() -> Any`：返回配置好的 ChatOpenAI 子类实例
  - `validate_model() -> bool`：通过 validators 模块验证模型
- `_resolve_provider_base_url(provider)`：解析提供商默认 base URL（支持环境变量覆盖）
- `_input_to_messages(input_)`：将 LangChain 输入统一转为消息列表

## 与其他模块的关系
- 依赖：`api_key_env.get_api_key_env`（查询密钥环境变量）、`base_client.BaseLLMClient/normalize_content`（基类和内容归一化）、`capabilities.get_capabilities`（模型能力查询）、`validators.validate_model`（模型验证）、`langchain_openai.ChatOpenAI`
- 被依赖：`factory.py`（通过 `create_llm_client` 路由创建）
