from __future__ import annotations
from typing import Dict, Any, List
import pandas as pd
from tools.prices import fetch_prices, quick_stats
from tools.news import get_symbol_news, load_news_from_csv

SENT_THRESH = {
    "very_bearish": -0.025,
    "bearish": -0.005,
    "bullish": 0.005,
    "very_bullish": 0.025,
}

class MarketAgent:
    """Market Agent handles price and news ingestion, classification, and summarization."""

    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg

    # Ingest prices and news
    def ingest_prices(self, symbol: str) -> pd.DataFrame:
        p = self.cfg.get("prices", {})
        return fetch_prices(symbol, p.get("period", "6mo"), p.get("interval", "1d"))

    def ingest_news(self, symbol: str) -> List[Dict[str, Any]]:
        n = self.cfg.get("news", {})
        provider = n.get("provider", "yfinance")
        if provider == "csv":
            return load_news_from_csv(n.get("csv_path", "data/sample_news.csv"), symbol, n.get("max_per_symbol", 15))
        return get_symbol_news(symbol, n.get("max_per_symbol", 15))

    # Preprocess text (simple lowercasing)
    def preprocess_texts(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out = []
        for it in items:
            title = (it.get("title") or "").strip()
            if not title:
                continue
            out.append({"title": title, "lower": title.lower(), **{k: v for k, v in it.items() if k not in ("title",)}})
        return out

    # Sentiment classification based on price trend
    def classify(self, price_stats: Dict[str, Any]) -> str:
        r20 = price_stats.get("ret_20d")
        if r20 is None:
            return "neutral"
        if r20 <= SENT_THRESH["very_bearish"]:
            return "very_bearish"
        if r20 <= SENT_THRESH["bearish"]:
            return "bearish"
        if r20 >= SENT_THRESH["very_bullish"]:
            return "very_bullish"
        if r20 >= SENT_THRESH["bullish"]:
            return "bullish"
        return "neutral"

    def extract(self, df_prices: pd.DataFrame) -> Dict[str, Any]:
        return quick_stats(df_prices)

    def summarize(self, symbol: str, stats: Dict[str, Any], news_items: List[Dict[str, Any]], sentiment: str, max_bullets: int = 6) -> str:
        """Produce a simple Markdown summary combining price stats and news."""
        bullets = []
        if stats.get("empty"):
            bullets.append("No recent price data available.")
        else:
            bullets.extend([
                f"As of **{stats['asof']}**, {symbol} closed at **{stats['close']:.2f}**.",
                f"20-day return: **{(stats['ret_20d']*100):.2f}%** | 5-day: **{(stats['ret_5d']*100):.2f}%**." if stats.get('ret_20d') is not None else "Return stats unavailable.",
                f"Volatility (20d, annualized): **{stats['vol_20']:.2f}**." if stats.get('vol_20') is not None else "Volatility unavailable.",
                f"Trend: **{stats['trend']}** | Sentiment: **{sentiment}**.",
            ])

        if news_items:
            bullets.append("Recent headlines:")
            for it in news_items[:max_bullets - len(bullets)]:
                title = it.get("title") or "(untitled)"
                pub = it.get("publisher") or ""
                link = it.get("link") or ""
                if link:
                    bullets.append(f"- {title} — *{pub}* → {link}")
                else:
                    bullets.append(f"- {title} — *{pub}*")

        bullets = bullets[:max_bullets]
        md = f"### {symbol}\n\n" + "\n".join([f"- {b}" for b in bullets]) + "\n"
        return md
