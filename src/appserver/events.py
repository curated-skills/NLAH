from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    if hasattr(value, "model_dump"):
        return _to_jsonable(value.model_dump())
    if hasattr(value, "dict"):
        return _to_jsonable(value.dict())
    return value


class EventLogger:
    def __init__(
        self,
        event_log_path: Path,
        printer: Callable[[dict[str, Any]], None],
    ) -> None:
        self.event_log_path = event_log_path
        self.printer = printer
        self.event_log_path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: str, **data: Any) -> dict[str, Any]:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **{key: _to_jsonable(value) for key, value in data.items()},
        }
        line = json.dumps(payload, ensure_ascii=True)
        with self.event_log_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        self.printer(payload)
        return payload
