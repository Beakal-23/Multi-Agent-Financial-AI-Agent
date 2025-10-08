# workflows/router.py
def route_item(item: dict) -> str:
    txt = (item.get("title") or item.get("text") or "").lower()
    if any(k in txt for k in ["10-k", "10q", "earnings", "eps", "revenue"]):
        return "earnings_analyzer"
    if any(k in txt for k in ["rally", "downgrade", "upgrade", "market", "fed"]):
        return "market_analyzer"
    return "news_analyzer"
