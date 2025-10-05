from __future__ import annotations
from typing import Dict
from utils.io import load_yaml
from utils.memory import JsonMemory
from agents.planner import Planner
from agents.dispatcher import Dispatcher
from agents.market import MarketAgent
from agents.evalopt import EvaluatorOptimizer
from core.types import Report


def run(config_path: str = "config/config.yml", rubric_path: str = "config/rubric.yml"):
    cfg: Dict = load_yaml(config_path)
    rubric: Dict = load_yaml(rubric_path)

    print("🚀 Starting Multi-Agent Financial Analysis System...")
    memory = JsonMemory(cfg.get("memory", {}).get("path", "memory.json"))

    planner = Planner(cfg)
    dag = planner.plan()
    print(f"✅ Planned {len(dag.tasks)} tasks.")
    print("First few task IDs:", list(dag.tasks.keys())[:10])

    dispatcher = Dispatcher(cfg)
    market = MarketAgent(cfg)
    evalopt = EvaluatorOptimizer(rubric, memory)

    reports: Dict[str, Report] = {}

    for task in dag.topological_order():
        kind = task.kind
        symbol = task.params.get("symbol")
        print(f"▶️ Executing task: {kind} for {symbol}")

        if dispatcher.should_skip(kind):
            print(f"⚠️ Skipping task: {kind} for {symbol}")
            continue

        if kind == "prices":
            df = market.ingest_prices(symbol)
            if df.empty:
                print(f"⚠️ No price data found for {symbol}")
            else:
                print(f"✅ Retrieved {len(df)} rows of price data for {symbol}")

        elif kind == "news":
            items = market.ingest_news(symbol)
            print(f"📰 Retrieved {len(items)} news items for {symbol}")

        elif kind == "summarize":
            df = market.ingest_prices(symbol)
            stats = market.extract(df)
            items = market.preprocess_texts(market.ingest_news(symbol))
            sentiment = market.classify(stats)
            md = market.summarize(symbol, stats, items, sentiment, cfg.get("summarizer", {}).get("max_bullets", 6))
            rep = reports.get(symbol) or Report(symbol=symbol)
            rep.sections["stats"] = stats
            rep.sections["news"] = items
            rep.sections["sentiment"] = sentiment
            rep.markdown = md
            reports[symbol] = rep
            print(f"🧾 Summary generated for {symbol}")

        elif kind == "evaluate":
            rep = reports.get(symbol)
            if not rep:
                print(f"⚠️ No report found for {symbol} during evaluation")
                continue
            score, suggestions = evalopt.score(rep.markdown, symbol, rep.sections.get("stats", {}))
            improved = evalopt.optimize(rep.markdown, suggestions)
            rep.markdown = improved
            evalopt.remember(symbol, score)
            print(f"🧠 Evaluation complete for {symbol} (score={score:.2f})")

               # === Final reporting ===
    if not reports:
        print("⚠️ No reports generated — check data availability or ticker symbols.")
    else:
        print("\n✅ Generated", len(reports), "reports.")
        print("\n✅ All tasks completed successfully.")
        return reports


if __name__ == "__main__":
    # Run the main workflow
    reports = run()

    # ======= Colored Output =======
    from utils.io import colorize_sentiment, colorize_trend

    for sym, rep in reports.items():
        print("#" * 40)
        print(f"📊 Report for {sym}")
        print("#" * 40)

        lines = rep.markdown.splitlines()
        for line in lines:
            # Color sentiment
            if "Sentiment:" in line:
                sentiment = line.split("Sentiment:")[-1].strip().strip(".")
                line = line.replace(sentiment, colorize_sentiment(sentiment))
            # Add colored trend arrow
            if "Trend:" in line:
                trend = line.split("Trend:")[-1].split("|")[0].strip()
                line = line.replace(trend, colorize_trend(trend))
            print(line)



