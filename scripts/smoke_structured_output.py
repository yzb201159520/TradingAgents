"""End-to-end smoke for structured-output agents against a real LLM provider.

Runs the three decision-making agents (Research Manager, Trader, Portfolio
Manager) directly with their structured-output bindings and prints the
typed Pydantic instance + the rendered markdown for each.  Use this to
verify a provider's native structured-output mode (json_schema for
OpenAI / xAI / DeepSeek / Qwen / GLM, response_schema for Gemini, tool-use
for Anthropic) returns clean instances on the schemas we ship.

Usage:
    OPENAI_API_KEY=... python scripts/smoke_structured_output.py openai
    GOOGLE_API_KEY=... python scripts/smoke_structured_output.py google
    ANTHROPIC_API_KEY=... python scripts/smoke_structured_output.py anthropic
    DEEPSEEK_API_KEY=... python scripts/smoke_structured_output.py deepseek

The script does NOT call propagate(), to keep the surface tight and the
cost low — it exercises only the three structured-output calls we just
added, plus the heuristic SignalProcessor.
"""

from __future__ import annotations

import argparse
import os
import sys

from tradingagents.agents.managers.portfolio_manager import create_portfolio_manager
from tradingagents.agents.managers.research_manager import create_research_manager
from tradingagents.agents.trader.trader import create_trader
from tradingagents.graph.signal_processing import SignalProcessor
from tradingagents.llm_clients import create_llm_client


PROVIDER_DEFAULTS = {
    "openai": ("gpt-5.4-mini", None),
    "google": ("gemini-2.5-flash", None),
    "anthropic": ("claude-sonnet-4-6", None),
    "deepseek": ("deepseek-chat", None),
    "qwen": ("deepseek-v4-flash", None),
    "glm": ("glm-5", None),
    "xai": ("grok-4", None),
}


# Minimal but realistic state for the three agents.
DEBATE_HISTORY = """
Bull Analyst: 分众传媒(002027.SZ)是中国梯媒绝对龙头，占据约95%电梯海报
市场份额。新消费品牌崛起带动广告投放回暖，境外市场(韩国、东南亚、中东)
点位持续扩张，提供增量收入。公司保持高分红率(近年超80%)，现金流稳定。

Bear Analyst: 宏观经济不确定性导致广告主预算收紧，互联网广告持续分流
品牌广告投放。影院广告业务受票房波动影响较大。境外扩张尚处投入期，
短期对利润有摊薄效应。
"""


def _make_rm_state():
    return {
        "company_of_interest": "002027.SZ",
        "investment_debate_state": {
            "history": DEBATE_HISTORY,
            "bull_history": "Bull Analyst: 分众传媒是中国梯媒绝对龙头...",
            "bear_history": "Bear Analyst: 宏观经济不确定性导致广告主预算收紧...",
            "current_response": "",
            "judge_decision": "",
            "count": 1,
        },
    }


def _make_trader_state(investment_plan: str):
    return {
        "company_of_interest": "002027.SZ",
        "investment_plan": investment_plan,
    }


def _make_pm_state(investment_plan: str, trader_plan: str):
    return {
        "company_of_interest": "002027.SZ",
        "past_context": "",
        "risk_debate_state": {
            "history": "Aggressive: lean in. Conservative: trim. Neutral: balanced sizing.",
            "aggressive_history": "Aggressive: ...",
            "conservative_history": "Conservative: ...",
            "neutral_history": "Neutral: ...",
            "judge_decision": "",
            "current_aggressive_response": "",
            "current_conservative_response": "",
            "current_neutral_response": "",
            "count": 1,
        },
        "market_report": "A股市场整体震荡，消费板块轮动。",
        "sentiment_report": "机构持仓稳定，北向资金小幅流入。",
        "news_report": "分众传媒发布三季报，营收同比微增。",
        "fundamentals_report": "毛利率约60%，ROE超20%，分红率超80%。",
        "investment_plan": investment_plan,
        "trader_investment_plan": trader_plan,
    }


def _print_section(title: str, content: str) -> None:
    bar = "=" * 70
    print(f"\n{bar}\n{title}\n{bar}\n{content}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("provider", choices=list(PROVIDER_DEFAULTS.keys()))
    parser.add_argument("--deep-model", default=None, help="Override deep_think_llm")
    parser.add_argument("--quick-model", default=None, help="Override quick_think_llm")
    args = parser.parse_args()

    default_model, _ = PROVIDER_DEFAULTS[args.provider]
    deep_model = args.deep_model or default_model
    quick_model = args.quick_model or default_model

    print(f"Provider: {args.provider}")
    print(f"Deep model:  {deep_model}")
    print(f"Quick model: {quick_model}")

    # Build the LLM clients via the framework's factory.
    deep_client = create_llm_client(provider=args.provider, model=deep_model)
    quick_client = create_llm_client(provider=args.provider, model=quick_model)
    deep_llm = deep_client.get_llm()
    quick_llm = quick_client.get_llm()

    # 1) Research Manager
    rm = create_research_manager(deep_llm)
    rm_result = rm(_make_rm_state())
    investment_plan = rm_result["investment_plan"]
    _print_section("[1] Research Manager — investment_plan", investment_plan)

    # 2) Trader (consumes RM's plan)
    trader = create_trader(quick_llm)
    trader_result = trader(_make_trader_state(investment_plan))
    trader_plan = trader_result["trader_investment_plan"]
    _print_section("[2] Trader — trader_investment_plan", trader_plan)

    # 3) Portfolio Manager (consumes both)
    pm = create_portfolio_manager(deep_llm)
    pm_result = pm(_make_pm_state(investment_plan, trader_plan))
    final_decision = pm_result["final_trade_decision"]
    _print_section("[3] Portfolio Manager — final_trade_decision", final_decision)

    # 4) SignalProcessor extracts the rating with zero LLM calls.
    sp = SignalProcessor()
    rating = sp.process_signal(final_decision)
    _print_section("[4] SignalProcessor → rating", rating)

    # 5) Lightweight checks: each rendered output should carry the expected
    #    section headers so downstream consumers (memory log, CLI display,
    #    saved reports) keep working.
    checks = [
        ("Research Manager", investment_plan, ["**Recommendation**:"]),
        ("Trader",           trader_plan,     ["**Action**:", "FINAL TRANSACTION PROPOSAL:"]),
        ("Portfolio Manager", final_decision, ["**Rating**:", "**Executive Summary**:", "**Investment Thesis**:"]),
    ]
    print("\n" + "=" * 70 + "\nStructure checks\n" + "=" * 70)
    failures = 0
    for name, text, required in checks:
        for marker in required:
            ok = marker in text
            print(f"  {'PASS' if ok else 'FAIL'}  {name}: contains {marker!r}")
            failures += int(not ok)

    print()
    if failures:
        print(f"Smoke FAILED: {failures} structure check(s) missing.")
        return 1
    print("Smoke PASSED: structured output → rendered markdown chain works for", args.provider)
    return 0


if __name__ == "__main__":
    sys.exit(main())
