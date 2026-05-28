# structured.py 逻辑说明

## 文件用途
提供结构化输出绑定和调用回退的共享辅助函数，将 Research Manager、Trader 和 Portfolio Manager 三个决策 Agent 的"绑定结构化输出 + 失败回退自由文本"模式集中实现，保持 Agent 工厂函数简洁并统一回退日志。

## 核心逻辑

### 统一的 Agent 结构化输出模式
三个决策 Agent 遵循相同的调用模式：
1. **创建阶段**：调用 `llm.with_structured_output(Schema)` 将 LLM 包装为返回类型化 Pydantic 实例的结构化模型。若供应商不支持（如旧版 Ollama 模型），绑定失败则跳过，Agent 将全程使用自由文本生成。
2. **调用阶段**：优先调用结构化模型，将返回的 Pydantic 实例通过 `render` 函数渲染为 Markdown。若结构化调用失败（弱模型返回格式错误的 JSON、供应商瞬态错误等），回退到普通 `llm.invoke` 自由文本调用，确保流程永不阻塞。

### 集中化的价值
- Agent 工厂函数只需调用 `bind_structured` 和 `invoke_structured_or_freetext`，无需重复编写绑定/回退逻辑。
- 所有三个 Agent 在回退触发时记录一致的警告日志，便于排查。

## 关键函数/类

### bind_structured(llm, schema, agent_name) -> Optional[Any]
- `llm: Any` — 原始 LLM 实例
- `schema: type[T]` — Pydantic BaseModel 子类（如 ResearchPlan、TraderProposal、PortfolioDecision）
- `agent_name: str` — Agent 名称，用于日志标识
- 返回 `llm.with_structured_output(schema)` 的结果，或供应商不支持时返回 `None`
- 捕获 `NotImplementedError` 和 `AttributeError`，记录警告日志

### invoke_structured_or_freetext(structured_llm, plain_llm, prompt, render, agent_name) -> str
- `structured_llm: Optional[Any]` — 结构化 LLM 实例（来自 `bind_structured`），为 None 时直接走自由文本路径
- `plain_llm: Any` — 原始 LLM 实例，用于回退
- `prompt: Any` — LLM 接受的输入（字符串或消息列表），同时传给结构化和自由文本路径
- `render: Callable[[T], str]` — 将 Pydantic 实例渲染为 Markdown 字符串的函数
- `agent_name: str` — Agent 名称，用于日志标识
- 返回 Markdown 字符串（结构化渲染结果或自由文本响应的 content）
- 结构化调用失败时记录警告并重试为自由文本

## 与其他模块的关系
- **依赖**：
  - `pydantic.BaseModel` — 类型约束
  - `logging` — 警告日志
- **被依赖**：
  - `managers/research_manager.py` — 导入 `bind_structured`, `invoke_structured_or_freetext`
  - `managers/portfolio_manager.py` — 导入 `bind_structured`, `invoke_structured_or_freetext`
  - `trader/trader.py` — 导入 `bind_structured`, `invoke_structured_or_freetext`
