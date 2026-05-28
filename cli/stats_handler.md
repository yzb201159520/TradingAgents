# cli/stats_handler.py 逻辑说明

## 文件用途
LangChain 回调处理器，通过线程安全的方式跟踪 LLM 调用次数、工具调用次数和 Token 使用量，为 CLI 底部状态栏提供实时统计信息。

## 核心逻辑

### StatsCallbackHandler
继承 `langchain_core.callbacks.BaseCallbackHandler`，实现三个关键回调：

1. **`on_llm_start`**：当 LLM 开始调用时，LLM 调用计数 +1。处理传统 LLM 接口。
2. **`on_chat_model_start`**：当聊天模型开始调用时，LLM 调用计数 +1。处理聊天模型接口（如 GPT-4、Claude 等）。
3. **`on_llm_end`**：当 LLM 调用结束时，从响应中提取 Token 使用统计：
   - 从 `LLMResult.generations[0][0].message` 获取 `AIMessage`
   - 从 `AIMessage.usage_metadata` 提取 `input_tokens` 和 `output_tokens`
   - 异常安全：如果响应结构不符合预期（IndexError/TypeError），静默跳过
4. **`on_tool_start`**：当工具开始执行时，工具调用计数 +1。
5. **`get_stats`**：返回当前统计快照字典（`llm_calls`、`tool_calls`、`tokens_in`、`tokens_out`）。

### 线程安全设计
所有计数器操作均通过 `threading.Lock` 保护，确保在多线程流式处理中的数据一致性。

## 关键函数/类

- **`StatsCallbackHandler(BaseCallbackHandler)`**：统计回调处理器
  - `__init__()`：初始化计数器和线程锁
  - `on_llm_start(serialized, prompts, **kwargs)`：LLM 调用开始回调，递增 `llm_calls`
  - `on_chat_model_start(serialized, messages, **kwargs)`：聊天模型调用开始回调，递增 `llm_calls`
  - `on_llm_end(response, **kwargs)`：LLM 调用结束回调，提取 Token 用量
  - `on_tool_start(serialized, input_str, **kwargs)`：工具调用开始回调，递增 `tool_calls`
  - `get_stats()`：返回当前统计字典（`llm_calls`、`tool_calls`、`tokens_in`、`tokens_out`）

## 与其他模块的关系
- **依赖**：
  - `langchain_core.callbacks.BaseCallbackHandler`：LangChain 回调基类
  - `langchain_core.outputs.LLMResult`：LLM 响应结果类型
  - `langchain_core.messages.AIMessage`：AI 消息类型（用于提取 Token 元数据）
  - `threading.Lock`：线程同步原语
- **被依赖**：
  - `cli/main.py`：在 `run_analysis()` 中创建 `StatsCallbackHandler` 实例，传入 `TradingAgentsGraph` 构造器和 `graph.stream()` 调用，用于实时统计展示
