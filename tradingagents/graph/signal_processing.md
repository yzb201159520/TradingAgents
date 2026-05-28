# signal_processing.py 逻辑说明

## 文件用途
从投资组合经理（Portfolio Manager）的最终决策文本中提取 5 级评级信号，供下游消费者使用。

## 核心逻辑

### 评级提取
`SignalProcessor.process_signal` 方法从 Portfolio Manager 的决策文本中提取核心评级。由于 Portfolio Manager 通过结构化输出（structured output）生成 `PortfolioDecision`，并渲染为包含 `**Rating**: X` 标题的 markdown 文本，评级信息已经确定性嵌入输出中，因此无需额外的 LLM 调用。

### 委托给通用解析器
实际解析逻辑委托给 `tradingagents.agents.utils.rating.parse_rating`，该函数采用两遍启发式策略：
1. 第一遍：搜索显式的 `Rating: X` 标签行（兼容 markdown 粗体和冒号/连字符分隔符）。
2. 第二遍：若未找到标签，在整个文本中搜索首个 5 级评级关键词。

### 5 级评级体系
Buy → Overweight → Hold → Underweight → Sell（从最看涨到最看跌）。

### 向后兼容性
`__init__` 接受 `quick_thinking_llm` 参数但不再使用，仅为保持旧版调用接口兼容。

## 关键函数/类

### `SignalProcessor`
- **参数**：`quick_thinking_llm`（已弃用，仅为向后兼容保留）
- **方法**：
  - `process_signal(full_signal: str) -> str` — 接收完整决策文本，返回 5 级评级之一（Buy / Overweight / Hold / Underweight / Sell）

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.utils.rating.parse_rating`（执行实际的评级解析逻辑）
- **被依赖**：
  - `trading_graph.py`（TradingAgentsGraph 通过 `self.signal_processor.process_signal()` 提取最终评级）
