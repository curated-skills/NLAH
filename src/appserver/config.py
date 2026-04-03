from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sysconfig

from .env import load_env


def _get_int(env: dict[str, str], key: str, default: int) -> int:
    value = env.get(key)
    if value is None or value == "":
        return default
    return int(value)


def _get_optional_float(env: dict[str, str], key: str) -> float | None:
    value = env.get(key)
    if value is None or value == "":
        return None
    return float(value)


@dataclass(frozen=True)
class ModelSpec:
    raw: str
    model_name: str
    reasoning_effort: str | None

    @classmethod
    def parse(cls, raw: str) -> "ModelSpec":
        model_name = raw.strip()
        reasoning_effort = None
        if "@" in model_name:
            model_name, reasoning_effort = model_name.rsplit("@", 1)
            model_name = model_name.strip()
            reasoning_effort = reasoning_effort.strip() or None
        if not model_name:
            raise ValueError("Model string cannot be empty.")
        return cls(raw=raw, model_name=model_name, reasoning_effort=reasoning_effort)


@dataclass(frozen=True)
class RunConfig:
    project_root: Path
    asset_root: Path
    runtime_policy_path: Path
    harness_specs: list[str]
    task_file: Path | None
    task_source: str
    task_text: str
    workspace: Path
    run_root: Path
    model: ModelSpec
    max_steps: int | None
    default_bash_timeout: int
    api_key: str | None
    api_base: str | None
    temperature: float | None

    @classmethod
    def from_args(cls, args, project_root: Path) -> "RunConfig":
        asset_root = cls._discover_asset_root(project_root)
        workspace = Path(args.workspace).expanduser().resolve()
        env = load_env(
            [
                project_root / ".env",
                workspace / ".env",
            ]
        )
        runtime_policy_raw = args.runtime_policy or "runtime-policy/SKILL.md"
        runtime_policy_path = Path(runtime_policy_raw).expanduser()
        if not runtime_policy_path.exists():
            runtime_policy_path = (asset_root / runtime_policy_path).resolve()
        elif not runtime_policy_path.is_absolute():
            runtime_policy_path = runtime_policy_path.resolve()

        if not workspace.exists() or not workspace.is_dir():
            raise ValueError(f"Workspace does not exist or is not a directory: {workspace}")
        prompt = (args.prompt or "").strip()
        task_file: Path | None = None
        task_source = "prompt"
        task_text = prompt
        if not task_text and args.task_file:
            task_file = Path(args.task_file).expanduser().resolve()
            if not task_file.exists():
                raise ValueError(f"Task file does not exist: {task_file}")
            task_source = "task_file"
            task_text = task_file.read_text(encoding="utf-8")
        if not task_text:
            raise ValueError("A task is required. Pass --prompt or --task-file.")

        model_raw = args.model or env.get("LINGUACLAW_MODEL")
        if not model_raw:
            raise ValueError("A model is required. Pass --model or set LINGUACLAW_MODEL.")
        model = ModelSpec.parse(model_raw)

        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_root = workspace / ".linguaclaw" / "runs" / run_id

        return cls(
            project_root=project_root,
            asset_root=asset_root,
            runtime_policy_path=runtime_policy_path,
            harness_specs=list(args.harness or []),
            task_file=task_file,
            task_source=task_source,
            task_text=task_text,
            workspace=workspace,
            run_root=run_root,
            model=model,
            max_steps=args.max_steps,
            default_bash_timeout=args.default_bash_timeout or _get_int(env, "LINGUACLAW_BASH_TIMEOUT_SECONDS", 300),
            api_key=env.get("LINGUACLAW_API_KEY") or None,
            api_base=env.get("LINGUACLAW_API_BASE") or None,
            temperature=_get_optional_float(env, "LINGUACLAW_TEMPERATURE"),
        )

    @staticmethod
    def _discover_asset_root(project_root: Path) -> Path:
        if (project_root / "runtime-policy").exists():
            return project_root
        installed_root = Path(sysconfig.get_path("data")) / "share" / "linguaclaw"
        if (installed_root / "runtime-policy").exists():
            return installed_root
        raise FileNotFoundError(
            "Could not locate LinguaClaw runtime assets. Expected runtime-policy/ under the repository root "
            "or under the installed share/linguaclaw directory."
        )
