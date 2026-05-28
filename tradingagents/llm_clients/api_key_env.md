# api_key_env.py 逻辑说明

## 文件用途
提供提供商名称到 API 密钥环境变量名的唯一映射表，是系统中"哪个提供商用哪个环境变量"的唯一真相来源（single source of truth）。

## 核心逻辑
1. 定义 `PROVIDER_API_KEY_ENV` 字典，键为提供商名称（小写），值为对应的环境变量名（字符串）或 `None`（表示不需要密钥，如 ollama）。
2. 对于双区域提供商（国际站与中国站），各自使用独立的环境变量名，因为两站账号不互通（如 `qwen` 用 `DASHSCOPE_API_KEY`，`qwen-cn` 用 `DASHSCOPE_CN_API_KEY`）。
3. `get_api_key_env(provider)` 函数根据提供商名称（不区分大小写）返回对应的环境变量名；未知提供商返回 `None`，调用方应将其理解为"无法检查密钥"而非"不需要密钥"。

## 关键函数/类
- `PROVIDER_API_KEY_ENV: dict[str, Optional[str]]`：提供商 -> 环境变量名映射表，包含 openai、anthropic、google、azure、xai、deepseek、qwen/qwen-cn、glm/glm-cn、minimax/minimax-cn、openrouter、ollama 共 14 个条目
- `get_api_key_env(provider: str) -> Optional[str]`：根据提供商名称查询对应的环境变量名

## 与其他模块的关系
- 依赖：无外部模块依赖
- 被依赖：`openai_client.py`（在构建客户端时读取密钥环境变量并自动注入）、CLI 的 `ensure_api_key` 工具函数（交互式提示用户设置密钥）
