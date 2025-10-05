from __future__ import annotations
from typing import Dict, List
from core.types import Task

class DAG:
    """
    Represents a Directed Acyclic Graph (DAG) of Tasks.
    Handles dependency resolution and topological ordering.
    """
    def __init__(self, tasks: List[Task]):
        self.tasks = {t.id: t for t in tasks}
        self._topo = None

    def topological_order(self) -> List[Task]:
        """Return tasks in dependency-resolved order."""
        if self._topo:
            return self._topo

        indeg: Dict[str, int] = {t_id: 0 for t_id in self.tasks}
        for t in self.tasks.values():
            for d in t.deps:
                indeg[t.id] += 1

        ready = [tid for tid, deg in indeg.items() if deg == 0]
        order: List[Task] = []

        while ready:
            cur = ready.pop()
            order.append(self.tasks[cur])
            for t in self.tasks.values():
                if cur in t.deps:
                    indeg[t.id] -= 1
                    if indeg[t.id] == 0:
                        ready.append(t.id)

        self._topo = order
        return order
