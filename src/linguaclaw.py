from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

__version__ = "0.1.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="linguaclaw",
        description="A Claude-Code-style agent harness implemented mostly in natural language.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser(
        "run",
        help="Run the thin LinguaClaw runtime on a prompt or task file.",
    )
    run_parser.add_argument(
        "--runtime-policy",
        "--system-prompt",
        dest="runtime_policy",
        default=None,
        help="Path to the runtime policy SKILL.md file.",
    )
    run_parser.add_argument(
        "--harness",
        action="append",
        default=[],
        help="Harness artifact, harness module, or SKILL path to load. May be passed multiple times.",
    )
    run_parser.add_argument(
        "--task-file",
        default=None,
        help="Path to the task markdown file.",
    )
    run_parser.add_argument(
        "--prompt",
        default=None,
        help="Inline task prompt. If provided, it takes precedence over --task-file.",
    )
    run_parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace directory for bash execution. Defaults to the current directory.",
    )
    run_parser.add_argument(
        "--model",
        default=None,
        help="LiteLLM model string, optionally with @reasoning-effort.",
    )
    run_parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="Optional hard cap on model turns. Defaults to no limit.",
    )
    run_parser.add_argument(
        "--default-bash-timeout",
        type=int,
        default=None,
        help="Default timeout in seconds for bash actions.",
    )
    run_parser.add_argument(
        "--json",
        action="store_true",
        help="Print the raw JSONL event stream instead of the default Rich CLI output.",
    )
    return parser


def _bootstrap_env(project_root: Path, workspace_arg: str) -> None:
    load_dotenv(project_root / ".env", override=False)
    workspace = Path(workspace_arg).expanduser()
    if workspace.is_dir():
        load_dotenv(workspace / ".env", override=False)
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command != "run":
        parser.print_help()
        return

    project_root = Path(__file__).resolve().parents[1]
    _bootstrap_env(project_root, args.workspace)

    if args.json:
        printer = lambda payload: print(json.dumps(payload, ensure_ascii=True))
    else:
        from rich_cli import RichEventPrinter

        printer = RichEventPrinter()

    from appserver import RunConfig, run_app

    config = RunConfig.from_args(args, project_root=project_root)
    raise SystemExit(run_app(config, printer))


if __name__ == "__main__":
    main()
