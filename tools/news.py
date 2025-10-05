from __future__ import annotations
from typing import List, Dict
import pandas as pd
import yfinance as yf

def get_symbol_news(symbol: str, max_items: int = 15) -> List[Dict]:
    """Fetch recent news headlines using yfinance's built-in .news property."""
    try:
        tk = yf.Ticker(symbol)
        items = tk.news or []
        rows = []
        for it in items[:max_items]:
            rows.append({
                "title": it.get("title"),
                "publisher": it.get("publisher"),
                "link": it.get("link"),
                "providerPublishTime": it.get("providerPublishTime"),
            })
        return rows
    except Exception:
        return []

def load_news_from_csv(path: str, symbol: str, max_items: int = 15) -> List[Dict]:
    """Fallback loader for CSV-based news."""
    try:
        df = pd.read_csv(path)
        if "symbol" in df.columns:
            df = df[df["symbol"] == symbol]
        df = df.head(max_items)
        return df.to_dict(orient="records")
    except Exception:
        return []
