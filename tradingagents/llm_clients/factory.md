# factory.py 逻辑说明

## 文件用途
提供 `create_llm_client` 工厂函数，根据提供商名称将请求路由到对应的 LLM 客户端实现，是系统创建 LLM 客户端的主入口。

## 核心逻辑
1. 定义 `_OPENAI_COMPATIBLE` 元组，列出所有使用 OpenAI 兼容 Chat Completions API 的提供商（openai、xai、deepseek、qwen/qwen-cn、glm/glm-cn、minimax/minimax-cn、ollama、openrouter），它们统一由 `OpenAIClient` 处理。
2. `create_llm_client(provider, model, base_url, **kwargs)` 函数的工作流程：
   - 将 `provider` 转为小写
   - 若属于 `_OPENAI_COMPATIBLE`，延迟导入 `OpenAIClient` 并创建实例（传入 provider 参数）
   - 若为 `anthropic`，延迟导入 `AnthropicClient`
   - 若为 `google`，延迟导入 `GoogleClient`
   - 若为 `azure`，延迟导入 `AzureOpenAIClient`
   - 其他值抛出 `ValueError`
3. 采用延迟导入（lazy import），避免模块导入时拉入重型 LLM SDK 或在 API 密钥缺失时报错，这对测试收集阶段尤其重要。

## 关键函数/类
- `create_llm_client(provider, model, base_url, **kwargs) -> BaseLLMClient`：工厂函数，根据 provider 创建对应的 LLM 客户端实例
  - `provider`：提供商名称字符串
  - `model`：模型标识符
  - `base_url`：可选的自定义 API 端点
  - `**kwargs`：传递给客户端的额外参数

## 与其他模块的关系
- 依赖：`base_client.BaseLLMClient`（类型注解）、四个具体客户端模块（延迟导入）
- 被依赖：Agent 配置层、CLI 入口等需要创建 LLM 实例的所有模块
