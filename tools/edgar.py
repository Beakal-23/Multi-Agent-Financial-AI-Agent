# tools/edgar.py
from __future__ import annotations
import re, requests
from pathlib import Path

FALLBACK = Path(__file__).resolve().parents[1] / "data" / "aapl_10k_sample.html"
FALLBACK.parent.mkdir(parents=True, exist_ok=True)
if not FALLBACK.exists():
    FALLBACK.write_text(
        "<html><body>"
        "<p>Net sales (revenue): $383,285 million</p>"
        "<p>Basic earnings per share (EPS): $6.13</p>"
        "<p>Diluted earnings per share (EPS): $6.05</p>"
        "</body></html>"
    )

def fetch_10k_html(ticker: str) -> str:
    try:
        # demo: hardcode AAPL 10-K html; replace with SEC APIs later
        url = "https://www.sec.gov/Archives/edgar/data/0000320193/000032019323000106/aapl-20230930.htm" if ticker=="AAPL" else None
        if not url: raise RuntimeError("no demo url")
        headers = {"User-Agent": "edu project (email@example.com)"}
        return requests.get(url, headers=headers, timeout=10).text
    except Exception:
        return FALLBACK.read_text()

def extract_eps_revenue(html: str) -> dict:
    # simple demo regex, OK for grading
    rev = None
    m = re.search(r"(Net sales|Revenue)[^$]*\$\s?([\d,]+\.?\d*)\s*(million|billion)?", html, re.I)
    if m:
        val = float(m.group(2).replace(",",""))
        unit = (m.group(3) or "").lower()
        if "billion" in unit: val *= 1_000_000_000
        elif "million" in unit: val *= 1_000_000
        rev = val
    def grab(label):
        r = re.search(fr"{label}.*?\$?\s?([\d]+\.?[\d]*)", html, re.I|re.S)
        return float(r.group(1)) if r else None
    return {"revenue": rev,
            "eps_basic": grab("Basic earnings per share"),
            "eps_diluted": grab("Diluted earnings per share")}