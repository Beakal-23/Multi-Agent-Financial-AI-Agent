from __future__ import annotations
from typing import Dict, List
from core.types import Task
from core.graph import DAG

class Planner:
    """
    Planner builds a Directed Acyclic Graph (DAG) of tasks
    for each symbol based on the configuration file.
    """
    def __init__(self, cfg: Dict):
        self.cfg = cfg

    def plan(self) -> DAG:
        steps = self.cfg.get("planner", {}).get("steps", ["prices", "news"])
        tickers: List[str] = self.cfg.get("universe", {}).get("tickers", [])

        tasks: List[Task] = []
        for sym in tickers:
            # Prices task
            tasks.append(Task(id=f"prices:{sym}", kind="prices", params={"symbol": sym}))

            # News task (depends on prices)
            tasks.append(Task(id=f"news:{sym}", kind="news", params={"symbol": sym}, deps=[f"prices:{sym}"]))

            # Summarize task (depends on both)
            tasks.append(Task(id=f"summarize:{sym}", kind="summarize", params={"symbol": sym},
                              deps=[f"prices:{sym}", f"news:{sym}"]))

            # Evaluate task (depends on summary)
            tasks.append(Task(id=f"evaluate:{sym}", kind="evaluate", params={"symbol": sym},
                              deps=[f"summarize:{sym}"]))

        return DAG(tasks)
