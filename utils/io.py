from __future__ import annotations
import yaml
from pathlib import Path
from typing import Dict

# utils/io.py
class Color:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"


def colorize_sentiment(sentiment: str) -> str:
    """Return sentiment text with terminal color."""
    s = sentiment.lower()
    if "bullish" in s:
        return f"{Color.GREEN}{sentiment}{Color.RESET}"
    elif "bearish" in s:
        return f"{Color.RED}{sentiment}{Color.RESET}"
    else:
        return f"{Color.YELLOW}{sentiment}{Color.RESET}"


def colorize_trend(trend: str) -> str:
    """Return a colored trend arrow + label."""
    t = trend.lower()
    if "up" in t:
        return f"{Color.GREEN}↑ Up{Color.RESET}"
    elif "down" in t:
        return f"{Color.RED}↓ Down{Color.RESET}"
    else:
        return f"{Color.YELLOW}→ Flat{Color.RESET}"

def load_yaml(path: str) -> Dict:
    """Load YAML configuration file."""
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
