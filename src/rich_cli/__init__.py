from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.panel import Panel


def _body(text: str) -> str:
    return text.strip() or "(empty)"


def _usage_lines(usage: dict[str, Any]) -> list[str]:
    return [
        f"prompt tokens: {usage.get('prompt_tokens', 0)}",
        f"completion tokens: {usage.get('completion_tokens', 0)}",
        f"total tokens: {usage.get('total_tokens', 0)}",
    ]


def _render_tool_result(message: dict[str, Any]) -> tuple[str, str]:
    tool_name = str(message.get("name") or "tool")
    content = message.get("content")
    try:
        payload = json.loads(content) if isinstance(content, str) else {}
    except json.JSONDecodeError:
        payload = {"raw": content}
    lines = [
        f"exit code: {payload.get('exit_code', '?')}",
        f"runtime: {payload.get('runtime', '?')}s",
        f"timed out: {'yes' if payload.get('timed_out', False) else 'no'}",
    ]
    stdout = str(payload.get("stdout", "")).strip()
    stderr = str(payload.get("stderr", "")).strip()
    if stdout:
        lines.extend(["", "stdout:", stdout])
    if stderr:
        lines.extend(["", "stderr:", stderr])
    if "raw" in payload and payload["raw"]:
        lines.extend(["", "content:", str(payload["raw"])])
    return f"TOOL RESULT: {tool_name}", "\n".join(lines)


class RichEventPrinter:
    def __init__(self) -> None:
        self.console = Console()

    def __call__(self, payload: dict[str, Any]) -> None:
        event = str(payload.get("event") or "")

        if event == "run.started":
            model = payload.get("model")
            workspace = payload.get("workspace")
            harnesses = payload.get("harnesses") or []
            harness_text = ", ".join(str(item) for item in harnesses) if harnesses else "(none)"
            self.console.print(f"[bold cyan]LinguaClaw[/bold cyan] model={model} workspace={workspace}")
            self.console.print(f"[dim]harnesses:[/dim] {harness_text}")
            return

        if event == "tool.started":
            tool = payload.get("tool")
            arguments = payload.get("arguments") or {}
            cmd = arguments.get("cmd", "")
            timeout_seconds = arguments.get("timeout_seconds")
            self.console.print(f"[bold yellow]{tool}[/bold yellow] timeout={timeout_seconds}s")
            if cmd:
                self.console.print(Panel(_body(str(cmd)), title="TOOL CALL"))
            return

        if event == "message.triggered":
            reason = str(payload.get("reason") or "")
            if reason in {"system_prompt", "compression_prompt"}:
                return
            role = str(payload.get("role") or "").lower()
            message = payload.get("message") or {}
            if role == "user":
                text = str(message.get("content") or "")
                self.console.print(Panel(_body(text), title="USER"))
                return
            if role == "assistant":
                title = "ASSISTANT"
                if reason == "compression_summary":
                    title = "COMPRESSED CONTEXT"
                text = str(message.get("content") or "")
                if text:
                    self.console.print(Panel(_body(text), title=title))
                return
            if role == "tool":
                title, body = _render_tool_result(message)
                self.console.print(Panel(body, title=title))
                return
            return

        if event == "context.compression_requested":
            usage_ratio = payload.get("usage_ratio")
            prompt_tokens = payload.get("prompt_tokens")
            context_window = payload.get("context_window")
            self.console.print(
                f"[bold blue]Compressing context[/bold blue] "
                f"usage={usage_ratio} prompt_tokens={prompt_tokens} window={context_window}"
            )
            return

        if event == "run.completed":
            finish_reason = payload.get("finish_reason", "unknown")
            usage = payload.get("usage") or {}
            total_tool_calls = payload.get("total_tool_calls", 0)
            lines = [f"finish reason: {finish_reason}", f"tool calls: {total_tool_calls}"]
            lines.extend(_usage_lines(usage))
            self.console.print(Panel("\n".join(lines), title="RUN SUMMARY", border_style="green"))
            return

        if event == "run.failed":
            reason = payload.get("reason", "unknown")
            error = payload.get("error")
            text = f"run failed: {reason}"
            if error:
                text += f"\n{error}"
            self.console.print(Panel(text, title="RUN FAILED", border_style="red"))
            return


__all__ = ["RichEventPrinter"]
