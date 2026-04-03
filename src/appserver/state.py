from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _json_dump(path: Path, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


@dataclass(frozen=True)
class RunPaths:
    run_root: Path
    params_path: Path
    messages_path: Path
    response_path: Path
    events_path: Path

    @classmethod
    def create(cls, run_root: Path) -> "RunPaths":
        paths = cls(
            run_root=run_root,
            params_path=run_root / "params.json",
            messages_path=run_root / "messages.json",
            response_path=run_root / "RESPONSE.md",
            events_path=run_root / "events.jsonl",
        )
        paths.run_root.mkdir(parents=True, exist_ok=True)
        return paths


class StateStore:
    def __init__(self, paths: RunPaths) -> None:
        self.paths = paths

    def initialize(self, payload: dict[str, Any]) -> None:
        self.paths.response_path.write_text("LinguaClaw run initialized.\n", encoding="utf-8")
        self.write_params(payload)
        self.write_messages([])

    def write_response(self, text: str) -> None:
        self.paths.response_path.write_text(text.rstrip() + "\n", encoding="utf-8")

    def write_params(self, payload: dict[str, Any]) -> None:
        snapshot = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        _json_dump(self.paths.params_path, snapshot)

    def write_messages(self, messages: list[dict[str, Any]]) -> None:
        _json_dump(self.paths.messages_path, messages)
