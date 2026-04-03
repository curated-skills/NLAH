from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values


def load_env(paths: list[Path]) -> dict[str, str]:
    merged: dict[str, str] = {}
    for path in dict.fromkeys(path.expanduser().resolve() for path in paths):
        if not path.is_file():
            continue
        merged.update({key: value for key, value in dotenv_values(path).items() if value is not None})
    return {**merged, **os.environ}
