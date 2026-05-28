# config.py 逻辑说明

## 文件用途
提供运行时配置的读取与修改接口，是系统各模块获取当前配置的唯一入口，在 `DEFAULT_CONFIG` 基础上支持浅合并式部分更新。

## 核心逻辑

本文件实现了一个全局单例配置管理模式：

1. **懒初始化**：模块级变量 `_config` 初始为 `None`，首次访问时通过 `initialize_config()` 从 `default_config.DEFAULT_CONFIG` 深拷贝生成，确保默认配置不被修改。

2. **浅合并更新**：`set_config()` 支持部分更新——当传入的键值对中值为字典类型且配置中对应键也是字典时，执行一层深度的 `dict.update()` 合并（保留未覆盖的嵌套键）；标量值则直接替换。这允许调用方仅更新感兴趣的配置项而无需提供完整配置。

3. **防御性拷贝**：`get_config()` 返回配置的深拷贝，`set_config()` 对传入字典也执行深拷贝，防止外部引用意外修改内部状态。

4. **模块加载时初始化**：文件末尾调用 `initialize_config()`，确保模块导入后配置立即可用。

### 配置更新示例
```python
# 仅覆盖 data_vendors 中的一个键，其余嵌套键保持默认
set_config({"data_vendors": {"core_stock_apis": "alpha_vantage"}})

# 直接替换标量值
set_config({"max_debate_rounds": 3})
```

## 关键函数/类

### `initialize_config()`
若全局配置 `_config` 为 `None`，则从 `DEFAULT_CONFIG` 深拷贝初始化。幂等操作，重复调用无副作用。

### `set_config(config: Dict)`
将传入的配置字典合并到全局配置中。字典值执行一层深度合并，标量值直接替换。使用 `deepcopy` 保护传入和内部数据。

### `get_config() -> Dict`
返回当前全局配置的深拷贝，确保调用方无法意外修改内部状态。若尚未初始化则自动触发初始化。

## 与其他模块的关系
- **依赖**：`copy.deepcopy`（标准库）、`tradingagents.default_config`（提供 `DEFAULT_CONFIG` 默认值源）
- **被依赖**：
  - `tradingagents.graph.trading_graph.py`：主图构建入口，导入 `set_config` 用于应用用户自定义配置
  - `tradingagents.agents.utils.agent_utils.py`：智能体工具函数，读取运行时配置
  - `tradingagents.agents.analysts/news_analyst.py`、`market_analyst.py`、`fundamentals_analyst.py`：各分析师模块，通过 `get_config()` 获取数据供应商等配置
  - `tests/test_dataflows_config.py`：配置模块单元测试
