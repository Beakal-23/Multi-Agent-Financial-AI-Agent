# workflows/prompt_chain.py
from __future__ import annotations
import pandas as pd
from tools.news import with_sentiment

def ingest_news(df: pd.DataFrame) -> pd.DataFrame:
    return df.copy()

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    # e.g., dedupe, lowercase, strip punctuation
    out = df.copy()
    out["title"] = out["title"].astype(str).str.strip()
    return out

def classify(df: pd.DataFrame) -> pd.DataFrame:
    return with_sentiment(df)

def extract(df: pd.DataFrame) -> pd.DataFrame:
    # toy “event” extractor by keyword (upgrade later)
    events = []
    for _, r in df.iterrows():
        title = r["title"].lower()
        if "probe" in title or "lawsuit" in title: evt = "regulatory"
        elif "rally" in title or "beat" in title:   evt = "market_positive"
        elif "delay" in title or "concerns" in title: evt = "supply_chain"
        else: evt = "other"
        events.append(evt)
    out = df.copy()
    out["event"] = events
    return out

def summarize(df: pd.DataFrame) -> dict:
    return {
        "sentiment_counts": df["label"].value_counts().to_dict(),
        "event_counts": df["event"].value_counts().to_dict(),
    }
