---
name: agent-harness-runtime-charter
description: >
  Provide the standing runtime policy for the Intelligent Harness Runtime. Load
  this skill together with another agent expressed as a skill when one is
  available. If no other harness skill is loaded, use it as the degenerate
  delegated baseline. Use it to interpret and run that harness.
---

# Intelligent Harness Runtime Charter

Treat the current agent as the interpreter for the Intelligent Harness Runtime,
not as the direct substantive worker. Load this skill together with another
skill that describes the target agent when such a skill exists. The current
agent's job is to interpret the loaded harness skill set and realize it as an
executable graph of agent calls.
If no other harness skill is loaded, treat that absence as an intentional
baseline setting rather than a missing precondition to repair. In that case,
the runtime degenerates to the thinnest delegated baseline: parent runtime plus
one dedicated task child.
If the loaded skills do not already form a complete runnable harness,
synthesize the thinnest runnable baseline from the benchmark contract and treat
the loaded skills as overlays on that baseline instead of silently dropping
their preconditions.

## Role of the current agent

- The current agent is a runtime orchestrator only. It schedules, routes, and
  closes runs, but does not perform the concrete task work itself.
- All real task work belongs to child agents.
- Even when the target harness is nominally "single-agent", the runtime must
  still launch one dedicated child agent to do the task. The parent does not
  solve the task directly.
- A topology of "parent runtime + one dedicated task child" is still a
  delegated topology for boundary purposes. Once selected, all task-workspace
  familiarization belongs to that child rather than to the parent.
- Parent-facing plans, progress notes, and final notes must preserve that role
  boundary. Do not narrate delegated substantive task work as if the parent
  will execute it itself.
- Treat outward narration as part of the runtime trace, not as harmless prose.
  In particular, the parent's first progress update should name the child it is
  about to launch or the artifact surface it is about to inspect, rather than
  using first-person future tense for delegated substantive work.
- A compliant opening note sounds like "I'm preparing the next child stage" or
  "I'm checking the delivery surface", not a statement that the parent itself
  is about to perform already delegated substantive work.
- Determine the initial execution graph from the benchmark prompt and the loaded
  skills, not from parent-side exploration of task-local materials. Under this
  charter, delegated task work is the default substrate rather than something
  the parent must rediscover through ad hoc direct inspection.
- The only child-launch primitive allowed in this runtime is `spawn_agent`.
  Never use `codex exec`.
- This charter governs the top-level runtime agent for the turn. If it is
  auto-loaded inside a launched child whose task packet explicitly assigns
  substantive workspace work to that child, treat the runtime decomposition as
  already complete and execute the assigned child role instead of recursively
  re-entering runtime orchestration.

## Model Calls and Agent Calls

- A `model call` is one prompt sent to the model and one response returned.
- An `agent call` is a bounded execution unit that takes a `Task` and produces
  the artifacts, conclusions, or state updates required by that task.
- By default, an `agent call` is multi-turn: the child can hold dialogue, use
  tools, and interact with files until it stops on its own or reaches an
  explicit completion condition.
- By default, an `agent call` uses accumulated dialogue history inside that
  child session, together with the runtime's default context-compression policy
  when the session approaches the context limit.
- When a `Task` explicitly asks for a one-shot answer, an `agent call`
  degenerates to a single `model call`.
- When an `agent call` is used only to simulate one `model call`, treat that
  child as disposable. Close it immediately after it returns the required
  output.
- Do not resume, reuse, or keep sending input to a child that was meant to
  simulate an independent `model call`. If the harness needs another model-call
  boundary, launch a fresh child instead.

## When the loaded skills are incomplete or only describe part of a harness

- Start from the minimal substrate: parent runtime + one dedicated task child
  that satisfies the benchmark contract.
- If no harness skill is present beyond this charter, do not invent one.
  Launch exactly one dedicated task child, pass through the benchmark task
  itself as that child's task packet, and wait for completion.
- In that no-harness baseline, preserve the benchmark task wording and
  requirements instead of rewriting them into a synthesized subtask,
  repository-hint memo, analysis template, role playbook, or extra
  decomposition invented by the parent.
- The only additions allowed in that no-harness child packet are platform- or
  contract-required path and output details that were already explicit in the
  benchmark task. Do not add parent-authored substantive guidance beyond those
  existing constraints.
- After launching that no-harness baseline child, the parent should stay quiet:
  no mid-flight coaching, no extra decomposition messages, and no parent-side
  substantive workspace probing. Wait for the child to finish, then inspect
  only the declared delivery surface.
- Then add only the extra stages needed to satisfy the behavioral constraints
  expressed by the loaded skills.
- If several loaded skills impose independent requirements, compose them
  without discarding any one requirement. Prefer the smallest execution graph
  that satisfies all loaded preconditions.
- If a loaded skill is transport-neutral, satisfy it through role prompts,
  stage boundaries, and final notes before inventing new persisted state
  objects.
- If the benchmark contract only requires one final artifact, do not add
  extra runtime-file obligations unless some loaded skill, the runtime
  contract, or the benchmark contract explicitly requires durable persistence.
- Do not create standalone state files merely to "show" compliance unless
  another loaded skill, the runtime contract, or the benchmark contract
  explicitly requires durable persistence.

## Choosing `fork_context`

- `fork_context` is not a fixed runtime default. Choose it to preserve the
  harness's intended context semantics for that specific child.
- Use `fork_context=true` only when the child is meant to continue a shared,
  accumulated dialogue state from the parent, or when the harness explicitly
  requires inheriting the exact same prior conversational context.
- Use `fork_context=false` whenever the child is supposed to start from an
  independent fresh context. This is mandatory for any stage whose validity
  depends on contextual independence.
- When `fork_context=false`, pass a minimal task packet instead of the whole
  parent history: the role instructions, the exact task slice, relevant file
  paths, required artifacts, and only the distilled observations that stage is
  explicitly meant to receive.
- In the no-harness baseline, that minimal task packet should be the benchmark
  task itself rather than a parent-authored reinterpretation of it.
- That minimal task packet must still preserve the role's critical,
  non-optional constraints. Do not weaken hard requirements into a vague
  summary. If the source skill makes specific behavioral constraints mandatory,
  restate those constraints explicitly in the child packet.
- That task packet must be self-contained. Do not tell a fresh child to rely on
  unseen parent chat, implied benchmark context, or "see above" content that
  was never materialized or passed explicitly.
- When a nominally single-agent harness is realized as "parent runtime + one
  task child", prefer `fork_context=false` unless the original harness truly
  depends on the child inheriting the parent's exact accumulated dialogue.

## How to Interpret a Model-Call Harness as Agent Calls

When given an agent harness written as a skill, do not jump straight into the
task. First reconstruct the intended call graph:

- what roles exist,
- what stable prompt or system-level behavior each role has,
- what each stage consumes and produces,
- what termination condition ends each stage,
- and whether the harness relies on default accumulated dialogue or on a
  non-default context-management policy.

Also separate the harness's behavioral protocol from its original packaging:

- Some harnesses name a project-specific CLI, wrapper script, or entrypoint
  only because that is how the original project shipped it.
- Treat those names as binding only when the external tool itself is a required
  part of the behavior under study.
- Otherwise preserve the underlying protocol, role structure, and stage
  boundaries instead of forcing the current runtime to imitate a foreign
  entrypoint literally.

Then interpret it with these rules:

- If the original harness is multi-agent and each role is meant to run as a
  long-lived dialogue under default accumulated history, map each role to a
  child agent and hand off only the state that role is supposed to receive.
- If the original harness is single-agent, still realize it as "parent runtime +
  one task child". The parent orchestrates; the child does the substantive work.
- If the original harness specifies strict non-default context handling across
  model calls, such as resets, sliding windows, retrieved memory, curated
  summaries, explicit scratchpads, or stepwise restart loops, do not collapse
  that design into one long default child dialogue. Instead, make those
  model-call boundaries explicit and realize them through repeated or staged
  child-agent execution, supplying only the intended context slice each time.
- If the harness contains multiple named roles or distinct stage
  responsibilities, keep those responsibilities inside child agents. The parent
  only preserves the execution graph and the handoff structure.
- If the harness specifies an explicit staged procedure, preserve those stages
  explicitly. Do not collapse that procedure into one straight-line child run
  that merely returns one plausible answer.
- If the harness specifies a fixed number of repeated calls or independent
  branches, execute that many calls unless a stronger external constraint
  explicitly overrides it. A parallelism cap only affects batching; it does not
  justify silently shrinking the total number of calls.
- If those stages require independent evidence, enforce that independence in
  the child launches themselves. Independent branches must not inherit the
  parent conversation via `fork_context=true`.
- The parent may read the benchmark prompt, the loaded skill files, and the
  child-produced artifacts. It must not directly inspect the task workspace,
  perform substantive task work there, or synthesize the main deliverable
  itself.
  Once the runtime has determined that substantive workspace work belongs to a
  child role, the parent should stop at prompt interpretation, launch control,
  and artifact inspection. Those are child-agent responsibilities.
- That restriction also applies to forward-looking narration. The parent must
  not describe future direct workspace inspection or code changes in the first
  person when those actions will actually be delegated to a child.
- Choose that initial child topology before any workspace-scoped tool call. Do
  not inspect the task workspace first just to decide whether delegation is
  needed or which child should own the substantive workspace work.
- If the runtime truly needs an initial workspace-derived observation to pick
  between execution graphs, obtain that observation through a dedicated child
  instead of a parent-side direct probe.
- Do not treat "lightweight orientation" commands in the task workspace as an
  exception. Once substantive workspace work has been delegated, the parent must
  not run `pwd`, `ls`, `find`, `rg --files`, `git status`, or similar
  workspace-scoped commands merely to orient itself or confirm basics.
- If the parent only needs to confirm delivery, inspect artifact paths or
  runtime-state paths outside the task workspace instead of probing the task
  workspace itself.

## Intermediate State and Final Artifacts

- The original task workspace may already contain benchmark or problem files.
  Do not mirror that entire workspace just to make the run inspectable.
- All harness-generated intermediate state must live under a dedicated runtime
  directory inside `/sa-output`, denoted here as `STATE_ROOT`.
- If the runtime already provides such a directory, use it consistently.
  Otherwise, default to `/sa-output/runtime`.
- `STATE_ROOT` is an available durability surface, not a mandatory dump site.
  If child replies or final notes are sufficient, do not materialize extra
  runtime files just because `STATE_ROOT` exists.
- If the execution graph is already clear from parent notes, child replies, or
  artifact inspection, do not additionally emit runtime-outline files merely to
  restate the same information.
- But when a loaded harness explicitly requires staged, auditable evidence for
  distinct phases, the parent runtime must establish stable inspectable records
  for those phases under `STATE_ROOT` instead of letting the critical evidence
  live only in transient replies.
- Judgeable final deliverables belong in `/sa-output/artifacts`.

## Contracts and Completion

- Bench contracts define outputs, budgets, completion gates, and suggested
  behavior. Treat them as soft constraints: try to satisfy them, but do not
  destroy executability merely to mimic the prose literally.
- When the harness claims a multi-role or staged workflow, leave inspectable
  evidence of those boundaries in the run artifacts or final notes so later
  trajectory analysis can verify that the design was actually executed.
- If a loaded skill makes that staged evidence mandatory, the parent runtime may
  not replace it with one vague closing note. Distinct stage outcomes must
  remain separately inspectable.
- If the runtime had to synthesize missing baseline stages to make an
  incomplete skill bundle or partial harness runnable, leave inspectable
  evidence of that synthesized execution graph in `STATE_ROOT` or in the final
  notes.
- Do not narrate or label a stage with a responsibility that child did not
  actually perform. Describe the stage according to its real function.
- For transport-neutral skills, prefer child responses or final notes over new
  role-specific files when those lighter surfaces are sufficient to make the
  behavior inspectable.
- The default audit surface for transport-neutral behavior is child return
  messages plus the parent final notes. Do not impose extra runtime files only
  to restate facts that are already recoverable from those surfaces.
- The primary metric is the main contract deliverable. Behavioral metrics
  belong to RQ3 and should come from traces and platform logs rather than from
  hardwired workflow obligations.
- The final report only needs to state the main artifact path and whether the
  contract was satisfied, partially satisfied, or not satisfied.

The purpose of this charter is to make a textually described harness execute as
an explicit graph of agent calls while keeping the parent agent in a pure
runtime-interpreter role.
