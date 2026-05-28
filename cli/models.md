# cli/models.py 逻辑说明

## 文件用途
定义 CLI 层使用的数据模型枚举，包括分析师类型和资产类型，为整个 CLI 交互流程提供类型安全的选项值。

## 核心逻辑

### AnalystType 枚举
继承 `str` 和 `Enum`，使枚举值可直接作为字符串使用（如 JSON 序列化、字典键查找）。
- `MARKET = "market"`：市场分析师
- `SOCIAL = "social"`：情绪分析师（值保持 "social" 以兼容已保存配置和字符串键调用；用户界面显示为 "Sentiment Analyst"）
- `NEWS = "news"`：新闻分析师
- `FUNDAMENTALS = "fundamentals"`：基本面分析师

### AssetType 枚举
同样继承 `str` 和 `Enum`。
- `STOCK = "stock"`：股票资产
- `CRYPTO = "crypto"`：加密货币资产

资产类型影响分析师选择：加密货币资产不提供基本面分析师选项（因财务报表数据不可用）。

## 关键函数/类

- **`AnalystType(str, Enum)`**：分析师类型枚举
  - `MARKET`：市场分析师
  - `SOCIAL`：情绪分析师（内部值为 "social"，保持向后兼容）
  - `NEWS`：新闻分析师
  - `FUNDAMENTALS`：基本面分析师
- **`AssetType(str, Enum)`**：资产类型枚举
  - `STOCK`：股票
  - `CRYPTO`：加密货币

## 与其他模块的关系
- **依赖**：
  - `enum.Enum`：标准库枚举基类
  - `pydantic.BaseModel`：已导入但当前未使用（预留扩展）
- **被依赖**：
  - `cli/utils.py`：使用 `AnalystType` 和 `AssetType` 构建分析师选择列表和资产类型检测
  - `cli/main.py`：使用 `AnalystType` 进行分析师状态管理和映射
