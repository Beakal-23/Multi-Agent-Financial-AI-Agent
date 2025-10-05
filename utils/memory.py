from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

class JsonMemory:
    """A simple JSON-based key–value store for agent memory."""

    def __init__(self, path: str):
        self.path = Path(path)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def _read(self) -> Dict[str, Any]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _write(self, obj: Dict[str, Any]):
        self.path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

    def update_key(self, key: str, value: Any):
        data = self._read()
        data[key] = value
        self._write(data)

    def get(self, key: str, default=None):
        return self._read().get(key, default)
