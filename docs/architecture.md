# Architecture

## Design Target

LinguaClaw is being built as a natural-language implementation of the Claude Code idea.
The goal is not to clone a proprietary product surface.
The goal is to preserve the useful shape of that experience while moving as much behavior as possible out of framework glue code and into reusable markdown artifacts.

The intended v0 formula is:

- `LiteLLM` for model routing.
- One model-visible tool: `bash`.
- A runtime policy plus reusable natural-language harness modules.
- A thin appserver that emits a structured JSONL event stream.
- A separate Rich CLI that renders those events for humans.

## Scope

This repository is responsible for:

- the public runtime package,
- the standing runtime policy,
- reusable harness modules,
- imported artifact-style harness references,
- and the public run contract for other repositories to call.

This repository is not the benchmark platform.
Benchmark ingestion, experiment sweeps, evaluation aggregation, and leaderboard-facing automation belong in a separate repository.

## Core Principles

### 1. Keep the runtime thin

The runtime should do only a few things:

- assemble the prompt stack,
- call LiteLLM,
- execute the action,
- append the event stream,
- and stop when the completion contract is satisfied.

Everything else should be pushed outward into markdown artifacts whenever that is practical.

### 2. Prefer markdown modules over new runtime features

If a new behavior can be expressed as:

- runtime policy,
- a reusable harness module,
- an artifact-style harness,
- or a peripheral tool skill,

then it should not become a new hard-coded runtime feature.

### 3. Use LiteLLM as the only model gateway

The runtime should not accumulate provider-specific adapters.
Model selection, credentials, and backend compatibility should be normalized through LiteLLM.

The intended CLI model notation is:

```bash
linguaclaw run \
  --model anthropic/claude-sonnet-4-5@reasoning-effort
```

The exact interpretation of the `@...` suffix can evolve, but the public architecture assumes one model string plus one optional effort/profile suffix rather than many provider-specific flags.

### 4. Keep the tool surface minimal

The first public runtime should expose one tool to the model:

```json
{
  "cmd": "git status --short",
  "timeout_seconds": 300
}
```

The `bash` tool contract is intentionally narrow:

- inputs:
  - `cmd`
  - `timeout_seconds`
- default timeout:
  - 300 seconds
- working directory:
  - if needed, encode it in the command itself, for example `cd /workspace && pytest`
- outputs:
  - `exit_code`
  - `stdout`
  - `stderr`
  - `runtime`

No separate `read`, `write`, `edit`, or `search` tools should be exposed in v0.
The model should perform those tasks through `bash`.

### 5. Use file-backed state

State should be durable, inspectable, and path-addressable.
If a plan, verdict, artifact index, or handoff matters, it should live in files rather than in the appserver's process memory alone.

This enables:

- long-horizon runs,
- restartability,
- trajectory inspection,
- future sandboxing,
- and delegation via child runs.

### 6. Separate the machine interface from the human interface

The appserver should be the core runtime surface.
It should print structured JSONL events.
The Rich CLI should be a renderer, not the control plane.

That split keeps the core scriptable and stable:

- machines can consume the JSONL directly,
- humans can use the Rich frontend,
- and future tools can replay or analyze the same event stream.

## Planned Repository Layout

```text
LinguaClaw/
├── src/
│   ├── linguaclaw.py
│   ├── appserver/
│   └── rich_cli/
├── runtime-policy/
│   └── SKILL.md
├── harnesses/
│   ├── modules/
│   └── artifacts/
├── tool-skills/
└── docs/
    ├── architecture.md
    ├── module-authoring.md
    └── roadmap.md
```

The high-level meaning of each top-level area is:

- `runtime-policy/`
  - the standing system behavior and interpreter charter.
- `harnesses/modules/`
  - reusable modules that are fully loaded into the prompt when selected.
- `harnesses/artifacts/`
  - artifact-style harness bundles and imported reference behaviors.
- `tool-skills/`
  - peripheral skills such as GitHub CLI wrappers that should use progressive disclosure.
- `src/linguaclaw.py`
  - the thin public entry module for the runtime CLI.
- `src/appserver/`
  - the future minimal runtime loop.
- `src/rich_cli/`
  - the future human-facing presentation layer.

## Runtime Surfaces

The public interface should center on one command of this shape:

```bash
linguaclaw run \
  [--runtime-policy runtime-policy/SKILL.md] \
  [--system-prompt runtime-policy/SKILL.md] \
  --module file-backed-state \
  --module verifier \
  --task-file task.md \
  --workspace /workspace \
  --model anthropic/claude-sonnet-4-5@reasoning-effort
```

The important design choice is that `--module` means full prompt inclusion.
Modules are treated as always-on prompt components for the run.

That differs from a `skill`:

- a `module` is pinned into context,
- a `skill` is discovered progressively and should load metadata first.

This distinction matters because LinguaClaw wants both:

- strong, explicit, fixed harness composition,
- and a path to lighter auxiliary skill discovery later.

## Prompt Stack

The runtime should assemble prompts in a stable order:

1. runtime policy,
2. tool contract,
3. state contract,
4. selected modules,
5. task file,
6. environment facts.

This layering keeps behavior legible.
The runtime policy defines the rules.
Modules add patterns.
The task file supplies the concrete objective.

## Appserver Design

The appserver should remain minimal.
Its job is to turn a run request into an evented loop.

The planned loop is:

1. resolve configuration,
2. load runtime policy and modules,
3. build the prompt stack,
4. call LiteLLM,
5. parse the next action,
6. execute `bash`,
7. append a JSONL event,
8. update state files,
9. lazily compress context when needed,
10. repeat until the model returns a terminal answer.

Representative event families:

- `run.started`
- `prompt.assembled`
- `model.requested`
- `model.completed`
- `tool.started`
- `tool.completed`
- `context.compressed`
- `run.completed`
- `run.failed`

The event stream is the primary runtime trace.
The Rich CLI should render it, but not define it.

## Context Management

The runtime should support automatic lazy compression.
The intended behavior is:

- keep the natural full trajectory while it fits,
- when the context budget approaches a threshold, compress old turns,
- write the compression result to a durable state file,
- continue from that summary plus recent turns.

Compression is a runtime responsibility because it depends on context budget.
The policy for what to preserve, however, should be shaped by the runtime policy and harness modules rather than by opaque hard-coded heuristics.

## Subagents

Subagents should not require a special in-process orchestration framework in v0.
The simplest public design is to let a run launch another run through `bash` by calling the same CLI again with a child task packet and a separate state surface.

That means delegation can be expressed as:

- a harness decision in markdown,
- a child task file,
- and a bash invocation of the same runtime.

This keeps the core architecture uniform.

## Multimodal Direction

Multimodal support is planned, but not as a large new tool surface.

The preferred first attempt is:

- discover files through `bash`,
- write a structured attachment manifest,
- let the runtime detect that manifest and inject matching image or video assets into the next LiteLLM request.

If that proves too brittle, LinguaClaw can add one thin helper later.
The default assumption, however, is still bash-first.

## Sandbox Direction

LinguaClaw should eventually support a thin sandbox wrapper.
The current plan is explicitly conservative:

- do not ship a large sandbox framework first,
- do not design around approval dialogs,
- and do not let sandbox work dominate the runtime architecture.

The first runtime can operate without Docker integration.
Later, the project can add a very thin sandbox layer after the appserver contract stabilizes.

## Imported Seed Materials

The current `runtime-policy/` and much of `harnesses/` were imported from prior research artifacts.
They are useful starting points, not final public contracts.

The intended normalization path is:

- preserve the original seed materials,
- document the public architecture around them,
- then gradually align the imported skills with the new bash-first, appserver-first runtime.

## Non-Goals For The First Public Runtime

The first public runtime should not try to be:

- a benchmark platform,
- a full approval system,
- a GUI-heavy framework,
- a provider-specific tool-calling matrix,
- or a large plugin platform.

The real target is narrower:

- one small runtime,
- one strong policy,
- one small action surface,
- and a large amount of behavior captured in markdown.
