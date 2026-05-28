# social_media_analyst.py 逻辑说明

## 文件用途
向后兼容桥接模块，将旧的 `social_media_analyst` 导入路径重定向到已重命名的 `sentiment_analyst` 模块。此模块将在未来版本中移除。

## 核心逻辑
1. 模块被导入时自动触发 `DeprecationWarning` 警告，提示用户使用 `tradingagents.agents.analysts.sentiment_analyst` 替代。
2. 从 `sentiment_analyst` 模块重新导出 `create_sentiment_analyst` 和 `create_social_media_analyst` 两个函数，确保旧代码无需修改即可继续运行。
3. 此模块本身不包含任何 Agent 逻辑，所有逻辑已在 `sentiment_analyst.py` 中实现。

## 关键函数/类
- 无自有函数/类。重新导出的符号：
  - **`create_sentiment_analyst`**：来自 `sentiment_analyst`，创建情绪分析师节点。
  - **`create_social_media_analyst`**：来自 `sentiment_analyst`，已弃用的兼容别名。

## 与其他模块的关系
- **依赖**：
  - `tradingagents.agents.analysts.sentiment_analyst`：实际逻辑所在模块。
  - `warnings`：标准库，用于发出弃用警告。
- **被依赖**：
  - 任何旧代码中通过 `from tradingagents.agents.analysts.social_media_analyst import ...` 导入的位置。
