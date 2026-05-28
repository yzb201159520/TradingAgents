# google_client.py 逻辑说明

## 文件用途
处理 Google Gemini 系列模型的客户端实现，包括内容归一化、thinking_level 到 API 参数的映射以及模型验证。

## 核心逻辑

### NormalizedChatGoogleGenerativeAI
重写 `invoke()` 方法，调用 `normalize_content()` 将 Gemini 3 模型返回的类型化内容块列表归一化为纯字符串。Gemini 3 模型返回 content 为 `[{"type": "reasoning", ...}, {"type": "text", "text": "..."}]` 格式，需要提取文本块拼接。

### thinking_level 映射
Google 不同代际模型对思考深度的 API 参数不同，`GoogleClient` 统一接收 `thinking_level` 关键字参数，在 `get_llm()` 中根据模型名称进行映射：

1. **Gemini 3 系列**（模型名含 `gemini-3`）：
   - 直接传递 `thinking_level` 参数
   - Gemini 3 Pro 不支持 "minimal" 级别，自动降级为 "low"
   - Gemini 3 Flash 支持 minimal/low/medium/high
2. **Gemini 2.5 及更早系列**：
   - 映射为 `thinking_budget` 参数
   - "high" -> `-1`（动态思考）
   - 其他级别 -> `0`（禁用思考）

### 统一 API 密钥处理
`api_key` 和 `google_api_key` 两种参数名均可使用，优先取 `api_key`，映射为 LangChain 的 `google_api_key` 参数。

## 关键函数/类
- `NormalizedChatGoogleGenerativeAI(ChatGoogleGenerativeAI)`：内容归一化的 Google 聊天模型
  - `invoke()`：归一化 content
- `GoogleClient(BaseLLMClient)`：Google Gemini 客户端
  - `__init__(model, base_url, **kwargs)`：初始化
  - `get_llm() -> Any`：返回配置好的 ChatGoogleGenerativeAI 实例，含 thinking_level 映射逻辑
  - `validate_model() -> bool`：通过 validators 模块验证模型

## 与其他模块的关系
- 依赖：`base_client.BaseLLMClient/normalize_content`、`validators.validate_model`、`langchain_google_genai.ChatGoogleGenerativeAI`
- 被依赖：`factory.py`（当 provider == "google" 时创建）
