---
name: file-backed-state-module
description: >
  Externalize every transferable piece of state into durable files so prompts,
  handoffs, replies, and promoted artifacts remain path-addressable across
  delegation and context compression.
---

# File-Backed State Module

Load this module whenever task state must survive long horizons, delegation, or
context compression.
Its purpose is narrow: decide how information becomes durable and transferable.

## State root

- Choose a dedicated root directory for harness-generated intermediate state and
  call it `STATE_ROOT`.
- `STATE_ROOT` must live under `/sa-output` and stay separate from the original
  task workspace.
- If the runtime already provides such a directory, use it. Otherwise, default
  to `/sa-output/runtime`.
- Benchmark or task-provided files may remain in their original workspace. Do
  not duplicate that entire workspace into `STATE_ROOT` just for inspection.
- Only newly produced intermediate objects, transformed outputs, annotations,
  summaries, or handoff materials belong in `STATE_ROOT`.
- Create `STATE_ROOT/RESPONSE.md` early and keep that path stable for the whole
  run. Update its contents as the authoritative runtime-level status record
  instead of creating it only opportunistically at the end.

## Core rule

Nothing is considered transferred until it is written to a durable file.

- If the parent gives a child a task prompt, that prompt must be written to
  `TASK.md` before the child starts.
- If the parent gives a child role instructions, stable constraints, or
  reusable guidance, that content must be written to `SKILL.md` or another
  explicitly referenced file before the child starts.
- If a child finishes, its reusable reply must be written to `RESPONSE.md`.
- If the parent runtime reaches a stable stage boundary or final state, its
  authoritative top-level status must be written to `STATE_ROOT/RESPONSE.md`.
- If one stage hands information to another stage, the transmitted content must
  exist as a named file before the receiver acts on it.
- If the handoff depends on pre-existing input files in the task workspace, you
  do not need to copy the source files themselves. It is enough to record stable
  paths and usage instructions in `TASK.md`.

Chat messages may announce or summarize state, but they are not authoritative
handoff objects until the same content is materialized in files.

## Canonical durable objects

- `TASK.md`: the exact task prompt for the current agent or stage.
- `SKILL.md`: stable behavioral instructions or role specification when such a
  file is needed.
- `RESPONSE.md`: the authoritative runtime-level completion or status statement
  at `STATE_ROOT/RESPONSE.md`, including the current run state and where the
  receiver should look next.
- `children/<id>/RESPONSE.md`: the child agent's own completion statement,
  including what it claims to have produced and where the receiver should look
  next.
- `artifacts/`: concrete deliverables that later stages or evaluators consume.
- `state/task_history.jsonl`: append-only log of launches, updates, promotions,
  and other durable state transitions.
- `artifacts/manifest.json`: index from logical artifact names to concrete file
  paths and short descriptions.
- `state/latest.json` or `state/checkpoints/<seq>.json` when a reader needs a
  compact current-state snapshot in addition to the append-only history.

## Transfer discipline

- Before any receiver acts, the sender must finish writing all required files.
- If the sender later adds clarifications, append them to `TASK.md` or a named
  addendum file and reference that addendum from `TASK.md`.
- Never rely on "the child saw it in chat" as a durable guarantee.
- When the parent reuses a child output, reopen `RESPONSE.md` and the referenced
  files rather than trusting memory.
- If a file is important to later evaluation, promote it into the artifact index
  instead of leaving it implicit in logs or chat.

## Per-child handoff directories

- `STATE_ROOT/TASK.md` may describe the parent runtime stage, but it is not a
  substitute for a launched child's own handoff files.
- Every launched child should have a dedicated directory
  `STATE_ROOT/children/<child_id_or_role>/`.
- Before launch, write the exact child task packet to
  `children/<id>/TASK.md`.
- If the child depends on stable role instructions or reusable constraints,
  write them to `children/<id>/SKILL.md` or another named file referenced from
  that task packet before the child starts.
- The child task packet must be self-contained. Do not rely on parent chat,
  implicit benchmark context, or "see above" references that the child cannot
  reopen by path.
- After completion, the child's reusable completion statement belongs in
  `children/<id>/RESPONSE.md`.

## Recovery discipline

- If a child claims completion but the required durable outputs are missing,
  partially written, unstable, or not recoverable by path, treat that child as
  not yet complete.
- When a child fails to leave durable outputs, recover by relaunching a child
  or issuing that child a narrowed retry task that explicitly repairs the
  missing durable outputs.
- The parent may repair runtime bookkeeping, manifests, or launch records, but
  it must not take over the child's substantive task work merely because the
  child's durable outputs are absent.
- If a worker failed to materialize a required patch, report, response, or
  other durable deliverable, the correct fallback is another child attempt, not
  parent-authored substitution.
- Record each such recovery decision in `state/task_history.jsonl` and reflect
  the latest authoritative state in `STATE_ROOT/RESPONSE.md`.

## Minimum bookkeeping expectations

- `state/task_history.jsonl` should record at least child launch, task-packet
  update, child completion, and artifact promotion events with real timestamps.
- Use one stable timestamp field name within a run, preferably `ts`, and record
  actual current UTC times. Do not use fixed placeholder times such as
  `2026-03-23T00:00:00Z`.
- Use one declared schema version for the run's durable state objects. If you
  need versioned schemas, add an explicit `schema_version` field rather than
  drifting implicitly across files.
- Keep the event schema stable within a run. Do not mix equivalent keys such as
  `ts` and `timestamp`, or alternate arbitrarily between `artifact` and `name`
  for the same promoted-object slot.
- Keep the durable schema stable across repeated runs that claim the same
  `schema_version`. Do not alternate between equivalent keys such as
  `producer`, `producing_child`, and `produced_by`, or between logical artifact
  names for the same semantic deliverable, unless you intentionally publish a
  schema migration.
- Prefer one canonical promoted-artifact event shape across those runs:
  `schema_version`, `ts`, `event`, `stage`, `child_id`, `logical_name`,
  `artifact_path`, and `producer`, with the same field names and value types
  each time.
- Do not move those canonical slots in and out of a generic `details` wrapper
  across runs. If `child_id` or `artifact_path` is a first-class field for one
  sample, keep it first-class for the others that claim the same schema.
- If later evidence corrects an earlier belief, append a correction event
  rather than mutating old history lines in place.
- `artifacts/manifest.json` should not stay empty once artifacts are promoted.
  Add entries for the final deliverable and any important promoted support file.
- `artifacts/manifest.json` should be a JSON object keyed by logical artifact
  name, not a list wrapper whose keys must be reconstructed externally.
- Each manifest entry should include at least the concrete path, a short
  description, the producing child or stage when known, and the creation time.
- Prefer one canonical manifest entry shape across repeated runs as well:
  `{ "path": ..., "description": ..., "producer": ..., "created_at": ... }`.
- For any recurring semantic deliverable, keep one stable logical key across
  repeated runs unless a stronger external contract explicitly requires a
  different name.
- If you need to change that shape or logical key, treat it as an explicit
  schema revision rather than silent drift.
- If you keep a snapshot such as `state/latest.json`, treat it as a derived
  convenience view. The append-only log remains the audit trail.

## Minimal layout contract

The following objects should exist whenever applicable:

```text
STATE_ROOT/
  TASK.md
  RESPONSE.md
  state/
    task_history.jsonl
  children/<id>/
    TASK.md
    SKILL.md
    RESPONSE.md
    artifacts/
  artifacts/
    manifest.json
/sa-output/artifacts/
```

The exact directory layout may be extended, but the transfer rules above should
remain invariant.
