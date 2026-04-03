from __future__ import annotations

import json
from typing import Any

from .config import RunConfig
from .events import EventLogger
from .model_gateway import LiteLLMGateway, litellm
from .module_loader import PromptDocument, load_harnesses, load_runtime_policy
from .state import RunPaths, StateStore
from .tool_bash import BASH_TOOL, run_bash_tool


COMPRESSION_PROMPT = (
    "Please compress the key information above into a summary that is about one tenth of the original length. "
    "Preserve the user's intent and the most important context as faithfully as possible, so that a later model "
    "can recover nearly all of the important information from the summary alone. Drop minor details that are not "
    "important for continuing the task."
)

COMPRESSION_TRIGGER_RATIO = 0.8


def _truncate_text(text: str, max_chars: int = 6000) -> str:
    if len(text) <= max_chars:
        return text
    head = text[: max_chars // 2]
    tail = text[-max_chars // 2 :]
    return f"{head}\n\n...[truncated]...\n\n{tail}"


def _render_message(message: dict[str, Any]) -> str:
    role = str(message.get("role") or "unknown").upper()
    content = message.get("content")
    pieces: list[str] = [f"{role}:"]
    if isinstance(content, str) and content.strip():
        pieces.append(content.strip())
    tool_calls = message.get("tool_calls") or []
    if tool_calls:
        pieces.append("tool_calls:")
        for tool_call in tool_calls:
            pieces.append(json.dumps(tool_call, ensure_ascii=True))
    if role == "TOOL":
        pieces.append(f"name={message.get('name')}")
        pieces.append(f"tool_call_id={message.get('tool_call_id')}")
    return "\n".join(pieces)


def _emit_message(
    events: EventLogger,
    step: int,
    reason: str,
    message: dict[str, Any],
) -> None:
    events.emit(
        "message.triggered",
        step=step,
        reason=reason,
        role=message.get("role"),
        message=message,
        rendered=_render_message(message),
    )


def _build_prompt(
    config: RunConfig,
    runtime_policy: PromptDocument,
    harnesses: list[PromptDocument],
    paths: RunPaths,
) -> str:
    harness_sections = "\n\n".join(
        f"# Harness: {harness.name}\nSource: {harness.path}\n\n{harness.text}" for harness in harnesses
    )
    runtime_note = """# Runtime Note

You are LinguaClaw, a thin natural-language harness runtime.
Use the provided `bash` tool for all workspace interaction.
When the task is complete, stop calling tools and answer directly in plain text.
Keep commands concise and grounded in the current workspace.
Treat references to unavailable tools or runtimes in imported documents as guidance, not as executable affordances.
"""
    environment_facts = f"""# Environment Facts

- `WORKSPACE`: {config.workspace}
- `RUN_ROOT`: {paths.run_root}
"""
    return "\n\n".join(
        section
        for section in [
            "# Runtime Policy\n\n" + runtime_policy.text,
            runtime_note,
            harness_sections,
            environment_facts,
        ]
        if section.strip()
    )


def _assistant_message(result) -> dict[str, Any]:
    message: dict[str, Any] = {"role": "assistant", "content": result.text or None}
    if result.tool_calls:
        message["tool_calls"] = result.tool_calls
    return message


def _new_messages_since_last_request(
    history: list[dict[str, Any]],
    last_request_history_len: int,
) -> list[dict[str, Any]]:
    if last_request_history_len <= 0:
        return history
    if len(history) < last_request_history_len:
        return history
    return history[last_request_history_len:]


def _custom_llm_provider(config: RunConfig) -> str | None:
    if config.api_base and "/" not in config.model.model_name:
        return "openai"
    return None


def _get_context_window(config: RunConfig) -> int | None:
    try:
        info = litellm.get_model_info(
            config.model.model_name,
            custom_llm_provider=_custom_llm_provider(config),
            api_base=config.api_base,
        )
        max_input_tokens = info.get("max_input_tokens") or info.get("max_tokens")
        if max_input_tokens:
            return int(max_input_tokens)
    except Exception:
        pass
    try:
        max_tokens = litellm.get_max_tokens(config.model.model_name)
        if max_tokens:
            return int(max_tokens)
    except Exception:
        pass
    return None


def _estimate_prompt_tokens(config: RunConfig, prompt_stack: str, history: list[dict[str, Any]]) -> int | None:
    messages = [{"role": "system", "content": prompt_stack}, *history]
    try:
        return int(
            litellm.token_counter(
                model=config.model.model_name,
                messages=messages,
                tools=[BASH_TOOL],
            )
        )
    except Exception:
        return None


def _compress_history(
    history: list[dict[str, Any]],
    config: RunConfig,
    gateway: LiteLLMGateway,
    events: EventLogger,
    prompt_stack: str,
    step: int,
) -> list[dict[str, Any]]:
    context_window = _get_context_window(config)
    prompt_tokens = _estimate_prompt_tokens(config, prompt_stack, history)
    if not context_window or not prompt_tokens:
        return history
    usage_ratio = prompt_tokens / context_window
    if usage_ratio < COMPRESSION_TRIGGER_RATIO:
        return history
    compression_prompt = {"role": "user", "content": COMPRESSION_PROMPT}
    compression_messages = [{"role": "system", "content": prompt_stack}, *history, compression_prompt]
    _emit_message(events, step, "compression_prompt", compression_prompt)
    events.emit(
        "context.compression_requested",
        prompt_tokens=prompt_tokens,
        context_window=context_window,
        usage_ratio=round(usage_ratio, 4),
    )
    try:
        result = gateway.generate(
            config.model,
            compression_messages,
        )
        summary = result.text.strip()
        if summary:
            compressed_history = [
                {
                    "role": "user",
                    "content": "Compressed summary of the prior conversation. Treat this as the authoritative context for continuing the task:\n\n"
                    + summary,
                }
            ]
            _emit_message(events, step, "compression_summary", compressed_history[0])
            events.emit(
                "context.compressed",
                replaced_messages=len(history),
                kept_messages=len(compressed_history),
                prompt_tokens=prompt_tokens,
                context_window=context_window,
                usage_ratio=round(usage_ratio, 4),
                usage=result.usage,
            )
            return compressed_history
    except Exception as error:  # pragma: no cover - defensive path
        events.emit(
            "context.compression_failed",
            error=str(error),
            prompt_tokens=prompt_tokens,
            context_window=context_window,
            usage_ratio=round(usage_ratio, 4),
            history_messages=len(history),
        )
    return history


def run_app(config: RunConfig, printer) -> int:
    runtime_policy = load_runtime_policy(config.runtime_policy_path)
    harnesses = load_harnesses(config.asset_root, config.harness_specs)
    paths = RunPaths.create(run_root=config.run_root)
    gateway = LiteLLMGateway(api_key=config.api_key, api_base=config.api_base, temperature=config.temperature)
    events = EventLogger(paths.events_path, printer)
    prompt_stack = _build_prompt(config, runtime_policy, harnesses, paths)
    state = StateStore(paths)
    state.initialize(
        {
            "started_at": paths.run_root.name,
            "status": "running",
            "workspace": str(config.workspace),
            "task_file": str(config.task_file) if config.task_file else None,
            "task_source": config.task_source,
            "model": config.model.raw,
            "runtime_policy": str(config.runtime_policy_path),
            "harnesses": [harness.name for harness in harnesses],
            "max_steps": config.max_steps,
            "default_bash_timeout": config.default_bash_timeout,
            "compression_trigger_ratio": COMPRESSION_TRIGGER_RATIO,
        }
    )

    events.emit(
        "run.started",
        model=config.model.raw,
        workspace=config.workspace,
        run_root=config.run_root,
        harnesses=[harness.name for harness in harnesses],
    )
    events.emit(
        "prompt.assembled",
        runtime_policy=config.runtime_policy_path,
        harnesses=[harness.name for harness in harnesses],
        system_prompt=prompt_stack,
    )

    _emit_message(events, 0, "system_prompt", {"role": "system", "content": prompt_stack})

    history: list[dict[str, Any]] = [{"role": "user", "content": config.task_text}]
    _emit_message(events, 0, config.task_source, history[0])
    state.write_messages(history)
    last_request_history_len = 0
    total_tool_calls = 0

    step = 1
    while True:
        if config.max_steps is not None and step > config.max_steps:
            break
        history = _compress_history(history, config, gateway, events, prompt_stack, step)
        state.write_messages(history)
        messages = [{"role": "system", "content": prompt_stack}, *history]
        new_messages = _new_messages_since_last_request(history, last_request_history_len)
        events.emit(
            "model.requested",
            step=step,
            model=config.model.raw,
            message_count=len(messages),
            new_message_count=len(new_messages),
            new_messages=new_messages,
        )
        last_request_history_len = len(history)
        try:
            result = gateway.generate(config.model, messages, tools=[BASH_TOOL])
        except litellm.AuthenticationError as error:
            events.emit("run.failed", reason="authentication_error", error=str(error))
            state.write_response(f"LinguaClaw run failed: authentication_error\n{error}\n")
            state.write_params({"status": "failed", "reason": "authentication_error"})
            return 1
        except Exception as error:
            events.emit("run.failed", reason="model_error", error=str(error))
            state.write_response(f"LinguaClaw run failed: model_error\n{error}\n")
            state.write_params({"status": "failed", "reason": "model_error"})
            return 1

        events.emit(
            "model.completed",
            step=step,
            finish_reason=result.finish_reason,
            usage=result.usage,
            tool_call_count=len(result.tool_calls),
        )
        total_tool_calls += len(result.tool_calls)
        assistant_message = _assistant_message(result)
        history.append(assistant_message)
        _emit_message(events, step, "assistant_response", assistant_message)

        if result.tool_calls:
            for tool_call in result.tool_calls:
                name = str(tool_call.get("function", {}).get("name") or "")
                raw_arguments = tool_call.get("function", {}).get("arguments") or "{}"
                try:
                    arguments = json.loads(raw_arguments)
                except json.JSONDecodeError:
                    arguments = {}
                events.emit("tool.started", step=step, tool=name, arguments=arguments)
                if name == "bash":
                    tool_result = run_bash_tool(arguments, config.workspace, config.default_bash_timeout)
                else:
                    tool_result = {
                        "exit_code": 2,
                        "stdout": "",
                        "stderr": f"Unsupported tool: {name}",
                        "runtime": 0.0,
                        "timed_out": False,
                    }
                tool_result["stdout"] = _truncate_text(str(tool_result.get("stdout", "")))
                tool_result["stderr"] = _truncate_text(str(tool_result.get("stderr", "")))
                history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id"),
                        "name": name,
                        "content": json.dumps(tool_result, ensure_ascii=True),
                    }
                )
                _emit_message(events, step, "tool_result", history[-1])
                state.write_params(
                    {
                        "status": "running",
                        "step": step,
                        "last_tool": name,
                        "last_exit_code": tool_result.get("exit_code"),
                    }
                )
                events.emit(
                    "tool.completed",
                    step=step,
                    tool=name,
                    exit_code=tool_result["exit_code"],
                    runtime=tool_result["runtime"],
                    timed_out=tool_result["timed_out"],
                )
            state.write_messages(history)
            step += 1
            continue

        final_text = (result.text or "").strip()
        if not final_text:
            final_text = "LinguaClaw run completed without a final text response."
        state.write_response(final_text)
        state.write_params(
            {
                "status": "completed",
                "step": step,
                "last_tool": None,
                "usage": result.usage,
            }
        )
        events.emit(
            "run.completed",
            step=step,
            summary=final_text,
            finish_reason=result.finish_reason,
            usage=result.usage,
            total_tool_calls=total_tool_calls,
        )
        return 0

    state.write_response("LinguaClaw run stopped before completion because max_steps was exceeded.\n")
    state.write_params({"status": "failed", "reason": "max_steps_exceeded", "max_steps": config.max_steps})
    events.emit("run.failed", reason="max_steps_exceeded", max_steps=config.max_steps)
    return 2
