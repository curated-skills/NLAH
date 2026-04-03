from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PromptDocument:
    name: str
    path: Path
    text: str


def load_runtime_policy(path: Path) -> PromptDocument:
    return PromptDocument(name="runtime-policy", path=path, text=path.read_text(encoding="utf-8"))


def _load_prompt_text(path: Path) -> str:
    sections = [path.read_text(encoding="utf-8")]
    references_dir = path.parent / "references"
    if references_dir.exists():
        for reference_path in sorted(references_dir.rglob("*.md")):
            relative = reference_path.relative_to(path.parent)
            sections.append(
                f"# Reference: {relative.as_posix()}\n\n{reference_path.read_text(encoding='utf-8')}"
            )
    return "\n\n".join(section.strip() for section in sections if section.strip())


def resolve_harness_path(asset_root: Path, spec: str) -> Path:
    raw = Path(spec).expanduser()
    if raw.exists() and raw.is_file():
        return raw.resolve()
    if raw.exists() and raw.is_dir():
        candidate = raw / "SKILL.md"
        if candidate.exists():
            return candidate.resolve()
    artifact_path = asset_root / "harnesses" / "artifacts" / spec / "SKILL.md"
    if artifact_path.exists():
        return artifact_path.resolve()
    module_path = asset_root / "harnesses" / "modules" / spec / "SKILL.md"
    if module_path.exists():
        return module_path.resolve()
    raise FileNotFoundError(f"Could not resolve harness, module, or SKILL path: {spec}")


def load_harnesses(asset_root: Path, specs: list[str]) -> list[PromptDocument]:
    documents: list[PromptDocument] = []
    for spec in specs:
        path = resolve_harness_path(asset_root, spec)
        name = path.parent.name
        documents.append(PromptDocument(name=name, path=path, text=_load_prompt_text(path)))
    return documents
