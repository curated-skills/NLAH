# Trajectory Schema

Each agent run writes a trajectory JSON file to `trajectories/trajectory_<timestamp>.json`.
In multi-candidate mode, each candidate run writes to
`trajectories/candidate_<N>_<timestamp>.json`.

## Top-Level Fields

```json
{
  "task": "string — the original task description",
  "start_time": "ISO 8601 timestamp",
  "end_time": "ISO 8601 timestamp",
  "provider": "string — LLM provider name (e.g. anthropic, openai)",
  "model": "string — model identifier",
  "max_steps": "integer — step budget",
  "success": "boolean — whether the task completed successfully",
  "final_result": "string | null — final summary text",
  "execution_time": "float — wall-clock seconds",
  "llm_interactions": [ ... ],
  "agent_steps": [ ... ]
}
```

## `llm_interactions` Entry

```json
{
  "timestamp": "ISO 8601",
  "provider": "string",
  "model": "string",
  "input_messages": [ { "role": "string", "content": "string" } ],
  "response": {
    "content": "string",
    "model": "string",
    "finish_reason": "string",
    "usage": {
      "input_tokens": "integer",
      "output_tokens": "integer",
      "cache_creation_input_tokens": "integer | null",
      "cache_read_input_tokens": "integer | null",
      "reasoning_tokens": "integer | null"
    },
    "tool_calls": [ { "call_id": "string", "name": "string", "arguments": {} } ]
  },
  "tools_available": ["string"]
}
```

## `agent_steps` Entry

```json
{
  "step_number": "integer",
  "timestamp": "ISO 8601",
  "state": "THINKING | CALLING_TOOL | REFLECTING | COMPLETED | ERROR",
  "llm_response": {
    "content": "string",
    "model": "string",
    "finish_reason": "string",
    "usage": { "input_tokens": "integer", "output_tokens": "integer" },
    "tool_calls": [ { "call_id": "string", "name": "string", "arguments": {} } ]
  },
  "tool_calls": [ { "call_id": "string", "name": "string", "arguments": {} } ],
  "tool_results": [
    { "call_id": "string", "success": "boolean", "result": "string", "error": "string | null" }
  ],
  "reflection": "string | null",
  "error": "string | null"
}
```

## Usage Notes

- Trajectory files are append-safe: each step is written incrementally during execution.
- `success: true` is set only when the task completion gate passes (including `must_patch`
  validation when enabled).
- Use trajectory files for debugging, auditing, and analysis of agent behavior.
- In multi-candidate mode, trajectory files for each run are independent and do not
  cross-reference each other.
