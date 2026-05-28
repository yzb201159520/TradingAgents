# base_client.py 逻辑说明

## 文件用途
定义 LLM 客户端的抽象基类 `BaseLLMClient` 和响应内容归一化工具函数 `normalize_content`，为所有具体提供商客户端提供统一接口和公共行为。

## 核心逻辑

### normalize_content 函数
多个提供商（OpenAI Responses API、Google Gemini 3 等）的 LLM 响应中 `content` 字段返回的是类型化块列表（如 `[{"type": "reasoning", ...}, {"type": "text", "text": "..."}]`），而下游 Agent 期望 `content` 为纯字符串。`normalize_content` 从块列表中提取 `type == "text"` 的文本并拼接，丢弃推理/元数据块，实现内容归一化。

### BaseLLMClient 抽象基类
1. 构造函数接收 `model`（模型名）、`base_url`（可选自定义端点）和 `**kwargs`（提供商特有参数），统一存储为实例属性。
2. `get_provider_name()`：返回提供商名称，优先取 `self.provider` 属性，否则从类名中去除 "Client" 后缀并转小写。
3. `warn_if_unknown_model()`：调用 `validate_model()` 检查模型是否在已知列表中，若不在则发出 `RuntimeWarning`，但不阻止执行——允许用户使用未知模型。
4. `get_llm()`（抽象方法）：子类必须实现，返回配置好的 LLM 实例。
5. `validate_model()`（抽象方法）：子类必须实现，验证模型是否受支持。

## 关键函数/类
- `normalize_content(response)`：将响应 content 从类型化块列表归一化为纯字符串
- `BaseLLMClient(ABC)`：LLM 客户端抽象基类
  - `__init__(model, base_url, **kwargs)`：初始化模型名、端点和额外参数
  - `get_provider_name() -> str`：获取提供商名称
  - `warn_if_unknown_model() -> None`：未知模型时发出警告
  - `get_llm() -> Any`（抽象）：返回配置好的 LLM 实例
  - `validate_model() -> bool`（抽象）：验证模型是否受支持

## 与其他模块的关系
- 依赖：`abc`、`typing`、`warnings`（标准库）
- 被依赖：所有具体客户端类（`OpenAIClient`、`AnthropicClient`、`GoogleClient`、`AzureOpenAIClient`）继承此类；`normalize_content` 被各 `Normalized*` 子类调用
