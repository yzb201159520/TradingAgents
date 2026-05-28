# azure_client.py 逻辑说明

## 文件用途
处理 Azure OpenAI 部署的客户端实现，是最简单的具体客户端，仅需内容归一化和环境变量配置。

## 核心逻辑

### NormalizedAzureChatOpenAI
重写 `invoke()` 方法，调用 `normalize_content()` 将 Azure OpenAI 返回的类型化内容块归一化为纯字符串，与 OpenAI Responses API 返回格式保持一致。

### AzureOpenAIClient
1. `get_llm()` 方法：
   - 调用 `warn_if_unknown_model()`（虽然 `validate_model()` 始终返回 True，此调用仍执行以保持接口一致）
   - 从环境变量 `AZURE_OPENAI_DEPLOYMENT_NAME` 读取 Azure 部署名称，若未设置则回退到模型名
   - 透传 `timeout`、`max_retries`、`api_key`、`reasoning_effort`、`callbacks`、`http_client`、`http_async_client` 等参数
   - 返回 `NormalizedAzureChatOpenAI` 实例
2. `validate_model()` 始终返回 `True`，因为 Azure OpenAI 接受任何已部署的模型名称——实际验证由 Azure 端完成。

### 所需环境变量
- `AZURE_OPENAI_API_KEY`：API 密钥
- `AZURE_OPENAI_ENDPOINT`：端点 URL（如 `https://<resource>.openai.azure.com/`）
- `AZURE_OPENAI_DEPLOYMENT_NAME`：部署名称（可选，默认使用模型名）
- `OPENAI_API_VERSION`：API 版本（如 `2025-03-01-preview`）

## 关键函数/类
- `NormalizedAzureChatOpenAI(AzureChatOpenAI)`：内容归一化的 Azure 聊天模型
  - `invoke()`：归一化 content
- `AzureOpenAIClient(BaseLLMClient)`：Azure OpenAI 客户端
  - `__init__(model, base_url, **kwargs)`：初始化
  - `get_llm() -> Any`：返回配置好的 AzureChatOpenAI 实例
  - `validate_model() -> bool`：始终返回 True（Azure 接受任何已部署模型名）

## 与其他模块的关系
- 依赖：`base_client.BaseLLMClient/normalize_content`、`validators.validate_model`、`langchain_openai.AzureChatOpenAI`
- 被依赖：`factory.py`（当 provider == "azure" 时创建）
