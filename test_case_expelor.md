这是一个开源项目tradingagent的本地clone，探索项目，为我寻找一下项目中是否有可运行的测试用例、验收基线，               以及怎么运行                                                                                                    
                                                                                                                    
● Explore(查找测试用例和验收基线)                                                                                   
  ⎿  Done (18 tool uses · 19.1k tokens · 1m 1s)                                                                   
  (ctrl+o to expand)                                                                                                
                                   
  Read 2 files, listed 1 directory (ctrl+o to expand)                                                               
                                                                                                                    
● TradingAgents 项目测试与运行情况                                                                                  
                                                                                                                    
  1. 测试用例（pytest）                                                                                             
                                                                                                                      测试目录：C:\data\project\TradingAgents\tests\，共 18 个测试文件 + conftest.py：                                  
                                                                                                                      ┌──────────────────────────────────────────────────────────────────────────────────────┬──────────────────────┐   
  │                                         文件                                         │         用途         │
  ├──────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┤
  │ test_analyst_execution.py                                                            │ 分析师执行流程       │
  ├──────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┤
  │ test_signal_processing.py                                                            │ 信号处理             │
  ├──────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┤
  │ test_model_validation.py                                                             │ 模型校验             │
  ├──────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┤
  │ test_checkpoint_resume.py                                                            │ LangGraph checkpoint │
  │                                                                                      │  恢复                │
  ├──────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┤
  │ test_crypto_asset_mode.py                                                            │ 加密资产模式         │
  ├──────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┤
  │ test_structured_agents.py                                                            │ 结构化输出 agent     │
  ├──────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┤
  │ test_capabilities.py                                                                 │ LLM 能力路由         │
  ├──────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┤
  │ test_api_key_env.py / test_env_overrides.py                                          │ 环境变量解析         │
  ├──────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┤
  │ test_anthropic_effort.py / test_deepseek_reasoning.py / test_minimax.py /            │ 各 LLM provider 适配 │
  │ test_google_api_key.py / test_ollama_base_url.py                                     │                      │
  ├──────────────────────────────────────────────────────────────────────────────────────┼──────────────────────┤
  │ test_memory_log.py / test_dataflows_config.py / test_safe_ticker_component.py /      │ 工具与配置           │
  │ test_ticker_symbol_handling.py                                                       │                      │
  └──────────────────────────────────────────────────────────────────────────────────────┴──────────────────────┘

  配置（pyproject.toml）：
  - testpaths = ["tests"]，addopts = "-ra --strict-markers"
  - markers：unit / integration / smoke
  - conftest.py 会自动注入占位 API key（防止 CI 因缺 key 卡住），并提供 mock_llm_client fixture——无 key
  也能跑单元测试

  没有 .github/workflows/、Makefile、tox.ini，也没有显式的 CI 流水线。

  2. 验收基线 / 冒烟脚本

  - main.py — 一键跑分析：TradingAgentsGraph("NVDA","2024-05-10")，需要真实 LLM key
  - cli/main.py — Typer 交互式 CLI，入口命令 tradingagents
  - scripts/smoke_structured_output.py — 端到端冒烟测试三个结构化 agent
  - test.py（根目录）— yfinance 手动验证脚本，与 pytest 无关
  - 无 examples/ / demo/ / notebook

  3. 怎么运行

  安装：
  pip install .              # 或 uv sync（项目自带 uv.lock）

  跑测试（无需 API key）：
  pytest                     # 全部
  pytest -m unit             # 仅单元测试
  pytest -m smoke
  pytest tests/test_signal_processing.py -v

  跑端到端基线（需真实 key，配置 .env，可参考 .env.example）：
  python main.py                              # 跑一次 NVDA 分析
  tradingagents                               # 交互式 CLI
  python scripts/smoke_structured_output.py   # 结构化 agent 冒烟
  docker compose run --rm tradingagents       # Docker 方式

  .env 至少需要其中一个 LLM key：OPENAI_API_KEY / GOOGLE_API_KEY / ANTHROPIC_API_KEY / DEEPSEEK_API_KEY 等；可用
  TRADINGAGENTS_* 变量覆盖默认 provider/model。

  跑端到端基线（需真实 key，配置 .env，可参考 .env.example）：
  python main.py                              # 跑一次 NVDA 分析
  tradingagents                               # 交互式 CLI
  python scripts/smoke_structured_output.py   # 结构化 agent 冒烟
  docker compose run --rm tradingagents       # Docker 方式

  .env 至少需要其中一个 LLM key：OPENAI_API_KEY / GOOGLE_API_KEY / ANTHROPIC_API_KEY / DEEPSEEK_API_KEY 等；可用
  TRADINGAGENTS_* 变量覆盖默认 provider/model。

  ---
  建议起步：先跑 pytest -m unit 验证环境（无需 key），再配 .env 跑 python scripts/smoke_structured_output.py
  做最小端到端验证，最后用 python main.py 跑完整决策。

  由于你只是在做项目探索（非实现任务），无需进入实施阶段；如需我针对某一部分（比如「补一条 CI
  流水线」「加端到端验收脚本」）做实施规划，再告诉我具体目标。

✻ Worked for 1m 47s

※ recap: 你想探索本地 clone 的 TradingAgents 项目里有哪些可运行的测试和验收基线、以及怎么跑。我已盘点完毕：测试在     tests/（pytest，无需真 key），基线脚本是 main.py、scripts/smoke_structured_output.py、CLI 
  tradingagents。下一步建议先跑 pytest -m unit 验证环境。 (disable recaps in /config)  