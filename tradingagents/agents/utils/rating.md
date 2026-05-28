# rating.py 逻辑说明

## 文件用途
定义系统全局共享的 5 级投资评级词汇表和确定性启发式评级解析函数，供 Research Manager、Portfolio Manager、信号处理器和记忆日志统一使用，避免各调用点评级定义漂移。

## 核心逻辑

### 5 级评级体系
评级从最看涨到最看跌依次为：Buy、Overweight、Hold、Underweight、Sell。这一有序元组 `RATINGS_5_TIER` 是系统中所有评级相关逻辑的唯一真实来源。

### 评级解析（两阶段策略）
`parse_rating` 从自由文本中提取评级，采用两阶段策略确保鲁棒性：
1. **标签优先**：查找 "Rating: X" / "rating - X" / "Rating: **X**" 等显式标签格式（容忍 Markdown 粗体包裹和冒号/连字符分隔符）。这一阶段优先因为标签上下文使匹配更可靠。
2. **全文扫描回退**：若未找到标签，逐行逐词扫描全文，找到第一个匹配 5 级词汇的单词（清理 `*:.,` 等标点后匹配）。

两个阶段均对大小写不敏感，返回 Title-cased 格式。若文本中无任何评级词汇，返回默认值 "Hold"。

## 关键函数/类

### RATINGS_5_TIER: Tuple[str, ...]
规范有序的 5 级评级元组：`("Buy", "Overweight", "Hold", "Underweight", "Sell")`

### _RATING_SET: Set[str]
评级词的小写集合，用于快速查找匹配。

### _RATING_LABEL_RE: Pattern
预编译正则，匹配 "Rating: X" 类标签格式。

### parse_rating(text, default="Hold") -> str
- `text: str` — 待解析的自由文本（通常是 Agent 输出的 Markdown）
- `default: str` — 未找到评级时的默认返回值，默认 "Hold"
- 返回 Title-cased 的评级字符串

## 与其他模块的关系
- **依赖**：无外部依赖（仅 `re`, `typing.Tuple`）
- **被依赖**：
  - `utils/memory.py` — 导入 `parse_rating`，用于从决策文本中提取评级标签
  - `graph/signal_processing.py` — 导入 `parse_rating`，用于从 Portfolio Manager 输出中提取评级供下游消费者使用
