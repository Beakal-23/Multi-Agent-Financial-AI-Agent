
from __future__ import annotations
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, Any
import warnings

# Suppress annoying FutureWarnings from yfinance
warnings.filterwarnings("ignore", category=FutureWarning)


def fetch_prices(symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """Fetch historical price data from Yahoo Finance."""
    df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.rename(columns=str.title)
    df["Return"] = df["Close"].pct_change()

    # Rolling statistics
    for w in (5, 20, 50):
        df[f"SMA_{w}"] = df["Close"].rolling(w).mean()
        df[f"Vol_{w}"] = df["Return"].rolling(w).std() * np.sqrt(252)

    return df.dropna().reset_index()


def quick_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute simple summary stats from a price DataFrame."""
    if df.empty:
        return {"empty": True}

    close_series = df["Close"]
    last_idx = len(close_series) - 1
    last_row = df.iloc[last_idx]

    # Safely compute returns as floats
    ret_5d = np.nan
    ret_20d = np.nan
    if len(close_series) > 5:
        ret_5d = float(close_series.iloc[last_idx] / close_series.iloc[last_idx - 5] - 1)
    if len(close_series) > 20:
        ret_20d = float(close_series.iloc[last_idx] / close_series.iloc[last_idx - 20] - 1)

    # Trend logic
    if np.isnan(ret_20d):
        trend = "flat"
    elif ret_20d > 0:
        trend = "up"
    elif ret_20d < 0:
        trend = "down"
    else:
        trend = "flat"

    # Volatility
    vol_20 = None
    if "Vol_20" in df.columns and not df["Vol_20"].empty:
        vol_20 = float(df["Vol_20"].iloc[last_idx])

    # --- Clean up 'Date' field safely ---
    date_value = last_row.get("Date", None)

    if isinstance(date_value, pd.Series):
        date_value = date_value.iloc[0]
    elif isinstance(date_value, (pd.DataFrame, dict)):
        date_value = list(date_value.values())[0] if len(date_value) > 0 else None

    try:
        asof = pd.to_datetime(date_value).strftime("%Y-%m-%d") if pd.notna(date_value) else "N/A"
    except Exception:
        asof = str(date_value)

    return {
        "asof": asof,
        "close": float(last_row["Close"]),
        "ret_5d": None if np.isnan(ret_5d) else ret_5d,
        "ret_20d": None if np.isnan(ret_20d) else ret_20d,
        "vol_20": vol_20,
        "trend": trend,
    }

