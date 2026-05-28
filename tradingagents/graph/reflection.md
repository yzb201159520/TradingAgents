# reflection.py 逻辑说明

## 文件用途
生成交易决策的事后反思，用于记忆日志（Memory Log）的延迟反思流程，将历史决策的实际收益结果转化为可复用的经验教训。

## 核心逻辑

### 延迟反思机制
反思不在交易决策执行时立即生成，而是延迟到下一次同一标的运行时才执行（Phase B）。这是因为决策的实际收益需要经过一定持仓期后才能获取。

### 反思生成流程
1. 系统在交易决策执行时仅记录决策文本（通过 `memory_log.store_decision`）。
2. 下一次同一标的运行时，`_resolve_pending_entries` 获取该标的的待处理条目。
3. 通过 yfinance 获取持仓期内的实际收益率（raw return）和超额收益（alpha return）。
4. 调用 `reflect_on_final_decision`，将决策文本与收益数据一同提交给 LLM。
5. LLM 根据 `_get_log_reflection_prompt` 中的指令，生成 2-4 句精炼反思。
6. 反思结果通过 `memory_log.batch_update_with_outcomes` 原子写入记忆日志。

### 反思提示词设计
反思提示词要求 LLM 按以下顺序覆盖三个要点：
1. 方向性判断是否正确（引用 alpha 数据）
2. 投资论点中哪些部分成立或失败
3. 一条可应用于未来类似分析的具体教训

输出要求为纯文本散文（2-4 句），不使用项目符号、标题或 markdown 格式，以保持紧凑性，避免在重新注入未来分析提示词时过度膨胀上下文窗口。

## 关键函数/类

### `Reflector`
- **参数**：`quick_thinking_llm`（用于生成反思的快速推理 LLM）
- **方法**：
  - `_get_log_reflection_prompt() -> str` — 返回反思提示词模板
  - `reflect_on_final_decision(final_decision, raw_return, alpha_return, benchmark_name="SPY") -> str`
    - `final_decision` — Portfolio Manager 的最终决策文本
    - `raw_return` — 标的原始收益率（如 +0.05 表示 5%）
    - `alpha_return` — 相对基准的超额收益率
    - `benchmark_name` — 基准标的名称（默认 SPY，对日本市场为 ^N225 等）
    - 返回 LLM 生成的反思文本

## 与其他模块的关系
- **依赖**：无外部模块依赖（仅使用 LLM 客户端）
- **被依赖**：
  - `trading_graph.py`（TradingAgentsGraph 初始化时创建 Reflector 实例，在 `_resolve_pending_entries` 中调用 `reflect_on_final_decision`）
