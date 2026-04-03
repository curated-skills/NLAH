from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any


BASH_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "bash",
        "description": "Run a bash command in the workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "cmd": {
                    "type": "string",
                    "description": "Bash command to execute. Use 'cd ... && ...' if you need another directory.",
                },
                "timeout_seconds": {
                    "type": "integer",
                    "description": "Optional timeout in seconds. Defaults to 300.",
                },
            },
            "required": ["cmd"],
            "additionalProperties": False,
        },
    },
}


def execute_bash(cmd: str, workspace: Path, timeout_seconds: int) -> dict[str, Any]:
    started_at = time.monotonic()
    try:
        completed = subprocess.run(
            ["bash", "-lc", cmd],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        runtime = time.monotonic() - started_at
        return {
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "runtime": round(runtime, 4),
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as error:
        runtime = time.monotonic() - started_at
        stdout = error.stdout if isinstance(error.stdout, str) else ""
        stderr = error.stderr if isinstance(error.stderr, str) else ""
        timeout_message = f"Command timed out after {timeout_seconds} seconds."
        stderr = f"{stderr}\n{timeout_message}".strip()
        return {
            "exit_code": 124,
            "stdout": stdout,
            "stderr": stderr,
            "runtime": round(runtime, 4),
            "timed_out": True,
        }


def run_bash_tool(arguments: dict[str, Any], workspace: Path, default_timeout: int) -> dict[str, Any]:
    cmd = str(arguments.get("cmd") or "").strip()
    timeout_value = arguments.get("timeout_seconds", default_timeout)
    try:
        timeout_seconds = int(timeout_value)
    except (TypeError, ValueError):
        timeout_seconds = default_timeout
    if not cmd:
        return {
            "exit_code": 2,
            "stdout": "",
            "stderr": "Missing required 'cmd' argument.",
            "runtime": 0.0,
            "timed_out": False,
        }
    return execute_bash(cmd=cmd, workspace=workspace, timeout_seconds=timeout_seconds)
