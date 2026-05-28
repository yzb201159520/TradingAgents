# capabilities.py 逻辑说明

## 文件用途
声明式的逐模型能力表，定义每个 OpenAI 兼容模型在 API 层面接受哪些参数、需要哪种结构化输出方法。这是系统中"哪个模型拒绝哪个参数"的唯一真相来源，客户端子类通过 `get_capabilities(model_name)` 查询能力而非硬编码模型名分支逻辑。

## 核心逻辑

### ModelCapabilities 数据类
使用 `@dataclass(frozen=True)` 定义不可变的能力描述，包含以下字段：
- `supports_tool_choice`：是否接受 `tool_choice` 参数
- `supports_json_mode`：是否支持 `response_format={"type":"json_object"}` 模式
- `supports_json_schema`：是否支持 `response_format={"type":"json_schema",...}` 模式
- `preferred_structured_method`：推荐的结构化输出方式（function_calling / json_mode / json_schema / none）
- `requires_reasoning_content_roundtrip`：是否需要在请求中回传上一轮推理内容（DeepSeek 思维模型）
- `requires_reasoning_split`：是否需要设置 `reasoning_split=True`（MiniMax M2.x 推理模型）

### 能力定义
1. **DeepSeek 思维模型**（`_DEEPSEEK_THINKING`）：接受 tools 数组但拒绝 tool_choice 参数；需要推理内容往返；使用 function_calling 方式
2. **DeepSeek 对话模型**（`_DEEPSEEK_CHAT`）：完全支持 tool_choice 和 json_mode；使用 function_calling 方式
3. **MiniMax 思维模型**（`_MINIMAX_THINKING`）：tool_choice 仅接受字符串枚举（"none"/"auto"），LangChain 的函数规范字典会触发 400；需要 reasoning_split；不支持 json_mode
4. **默认能力**（`_DEFAULT`）：全部支持，使用 function_calling 方式

### 查找策略
`get_capabilities(model_name)` 的查找顺序：
1. 精确 ID 匹配（`_BY_ID` 字典）：优先级最高
2. 正则模式匹配（`_BY_PATTERN` 列表）：前向兼容，如 `deepseek-v5-*`、`MiniMax-M3*` 等未来变体自动继承对应的能力
3. 返回默认能力（`_DEFAULT`）

### 已注册的精确模型 ID
- DeepSeek：deepseek-chat、deepseek-reasoner、deepseek-v4-flash、deepseek-v4-pro
- MiniMax：MiniMax-M2.7、MiniMax-M2.7-highspeed、MiniMax-M2.5、MiniMax-M2.5-highspeed、MiniMax-M2.1、MiniMax-M2.1-highspeed、MiniMax-M2

### 前向兼容模式
- `^deepseek-v\d` -> DeepSeek 思维模型能力
- `^deepseek-reasoner` -> DeepSeek 思维模型能力
- `^MiniMax-M\d` -> MiniMax 思维模型能力

## 关键函数/类
- `ModelCapabilities`（dataclass）：模型能力描述
- `StructuredMethod`：结构化输出方式类型（function_calling / json_mode / json_schema / none）
- `get_capabilities(model_name) -> ModelCapabilities`：根据模型名查询能力，精确匹配优先，模式匹配次之，默认兜底

## 与其他模块的关系
- 依赖：无外部模块依赖（仅标准库 `re`、`dataclasses`）
- 被依赖：`openai_client.py` 中的 `NormalizedChatOpenAI.with_structured_output()` 和 `MinimaxChatOpenAI._get_request_payload()` 查询能力表以决定参数和行为
