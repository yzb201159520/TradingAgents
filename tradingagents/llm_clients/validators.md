# validators.py 逻辑说明

## 文件用途
提供模型名称验证功能，检查给定的模型名称是否属于指定提供商的已知模型列表，用于在客户端初始化时发出警告提示。

## 核心逻辑

### VALID_MODELS 字典
从 `model_catalog.get_known_models()` 构建已知模型列表，但排除两个特殊提供商：
- **ollama**：用户可拉取任意本地模型，无法穷举
- **openrouter**：模型目录通过 API 动态获取，不在静态列表中

### validate_model 函数
1. 将 provider 转为小写
2. 对于 ollama 和 openrouter，直接返回 `True`——这两个提供商接受任何模型名
3. 若 provider 不在 `VALID_MODELS` 中（如新增的未知提供商），也返回 `True`——避免误拦
4. 否则检查 model 是否在对应提供商的已知模型列表中，返回布尔结果

### 验证结果的使用
验证结果仅在 `BaseLLMClient.warn_if_unknown_model()` 中使用：若模型不在已知列表中，发出 `RuntimeWarning` 但不阻止执行。这允许用户使用新发布的模型或自定义模型 ID，同时获得可能拼写错误的提醒。

## 关键函数/类
- `VALID_MODELS: dict[str, list[str]]`：排除 ollama/openrouter 后的已知模型列表
- `validate_model(provider, model) -> bool`：验证模型名是否在提供商的已知列表中
  - `provider`：提供商名称（不区分大小写）
  - `model`：模型标识符

## 与其他模块的关系
- 依赖：`model_catalog.get_known_models`（获取模型列表数据源）
- 被依赖：所有具体客户端类（`OpenAIClient.validate_model()`、`AnthropicClient.validate_model()`、`GoogleClient.validate_model()`）通过 `BaseLLMClient.warn_if_unknown_model()` 间接调用
