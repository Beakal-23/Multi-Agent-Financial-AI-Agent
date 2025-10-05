from __future__ import annotations
from typing import Dict, Any, List, Tuple
import time

class EvaluatorOptimizer:
    """
    Evaluator-Optimizer Agent
    Evaluates generated reports against rubric criteria
    and appends improvement suggestions if score < threshold.
    """

    def __init__(self, rubric: Dict[str, Any], memory):
        self.rubric = rubric.get("rubric", [])
        self.memory = memory

    def score(self, report_md: str, symbol: str, stats: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """Evaluate a report and return (score, improvement_suggestions)."""
        issues = []
        total, weight_sum = 0.0, 0.0

        for item in self.rubric:
            w = float(item.get("weight", 0.25))
            cid = item.get("id")
            weight_sum += w
            s = 0.7  # base score

            if cid == "coverage":
                needs = ["return", "volatility", "trend", "sentiment"]
                have = all(n in report_md.lower() for n in needs)
                s = 0.9 if have else 0.5

            elif cid == "recency":
                s = 0.9 if stats and stats.get("asof") else 0.6

            elif cid == "correctness":
                s = 0.85 if "closed at" in report_md else 0.6

            elif cid == "actionability":
                s = 0.75 if "recent headlines" in report_md else 0.6

            total += s * w

        final = total / (weight_sum or 1.0)
        if final < 0.8:
            issues.append({"symbol": symbol, "suggestion": "Add clearer takeaways or benchmark comparisons."})

        return final, issues

    def optimize(self, report_md: str, suggestions: List[Dict[str, Any]]) -> str:
        """Append improvement suggestions to the report."""
        if not suggestions:
            return report_md
        addendum = "\n\n> Improvements for next run: " + "; ".join(s["suggestion"] for s in suggestions)
        return report_md + addendum

    def remember(self, symbol: str, score: float):
        """Persist a memory record of the last evaluation score."""
        self.memory.update_key(f"score:{symbol}", {"ts": int(time.time()), "score": score})
