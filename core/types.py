from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class Task:
    """A unit of work in the agent system."""
    id: str
    kind: str                # e.g. prices | news | summarize | evaluate
    params: Dict[str, Any] = field(default_factory=dict)
    deps: List[str] = field(default_factory=list)  # dependent task IDs

@dataclass
class Artifact:
    """A product/result of a completed task."""
    type: str                # e.g. prices | news | summary | eval
    key: str                 # e.g. ticker symbol
    content: Any
    meta: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Report:
    """Final structured report combining task outputs."""
    symbol: str
    sections: Dict[str, Any] = field(default_factory=dict)
    markdown: str = ""
