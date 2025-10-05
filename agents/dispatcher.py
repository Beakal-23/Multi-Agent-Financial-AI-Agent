from __future__ import annotations
from typing import Dict, Any
from core.types import Artifact

class Dispatcher:
    """
    Dispatcher determines which agent handles which artifact
    (market, news, filing, etc.) and builds artifacts for them.
    """
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg

    def route_kind(self, kind: str) -> str:
        mapping = self.cfg.get("routing", {}).get("map", {})
        route = mapping.get(kind)
        if not route:
            print(f"⚠️ Unknown task kind: {kind} — using fallback route.")
            route = self.cfg.get("routing", {}).get("fallback", "skip")
        else:
            print(f"🔀 Routing kind '{kind}' → '{route}'")
        return route

    def should_skip(self, kind: str) -> bool:
        return self.route_kind(kind) == "skip"

    def build_artifact(self, kind: str, key: str, content: Any, meta: Dict[str, Any] | None = None) -> Artifact:
        return Artifact(type=kind, key=key, content=content, meta=meta or {})
