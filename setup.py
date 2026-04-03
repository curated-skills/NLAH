from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from setuptools import setup


ROOT = Path(__file__).resolve().parent
ASSET_ROOTS = ("runtime-policy", "harnesses", "tool-skills")


def collect_data_files() -> list[tuple[str, list[str]]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for root_name in ASSET_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(ROOT)
            target = Path("share/linguaclaw") / relative.parent
            grouped[str(target)].append(str(relative))
    return sorted((target, sorted(files)) for target, files in grouped.items())


setup(data_files=collect_data_files())
