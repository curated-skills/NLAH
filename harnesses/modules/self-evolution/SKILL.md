---
name: self-evolution-module
description: >
  Run a reflection-driven retry loop that improves later attempts along three
  axes: prompt evolution, tool evolution, and workflow evolution.
---

# Self-Evolution Module

Load this module when repeated attempts may benefit from changing how the task
is framed, what tools are available, or how the work is organized.
This module requires a reflection-driven retry loop rather than a one-off
cosmetic retry.

## Attempt loop

- Use a retry loop with an explicit attempt counter.
- The default maximum is 5 attempts unless the user or task contract specifies
  another bound.
- Attempt 1 is the baseline attempt. Do not invent a fake retrospective before
  that baseline exists.
- After every non-successful, partially successful, unstable, or stalled
  attempt, produce a reflection and use it to redesign the next attempt.
- Continue until success is actually judged or the attempt cap is reached.
  Do not stop early merely because an intermediate attempt "looks better" if
  the success condition has not yet been satisfied.

## Success trigger

- Count an attempt as successful only when the task's own acceptance gate has
  been met, such as a verifier verdict of `解决`, passing required checks, or
  another explicit completion condition.
- If the outcome is ambiguous, unverified, or still missing a required gate,
  treat it as not yet successful and continue the loop.

## Reflection trigger

- If even one real attempt has not yet finished, the trigger has not fired.
  Run the baseline attempt first, then reflect only on the concrete failure
  signals or instabilities that attempt actually exposed.
- Do not use this module to justify a preloaded reviewer or verifier gate before
  the first attempt. Ordinary staged execution is workflow design; self-
  evolution starts only when the trajectory has already told you what the next
  attempt should change.

Before planning the next attempt, review the trajectory so far:

- What actually failed?
- What partially worked and should be preserved?
- Where did time or budget go?
- What assumption turned out false?

A practical loop is:

- Draft or finish one attempt.
- Critique that attempt against concrete observed failures.
- Revise only the parts that the critique actually invalidates.

Repeat that loop while it keeps surfacing actionable failure signals and the
success condition is still unmet.

## Second-attempt optimization requirement

- The second attempt is the first mandatory optimization opportunity.
- A compliant second attempt must be materially shaped by the reflection from
  attempt 1. It should not be a cosmetic restatement of the same prompt with no
  real change in decision boundary, tool use, or workflow.
- The reflection for attempt 1 should explicitly explain why the next attempt
  is expected to do better.

## Evolution axis 1: Prompt evolution

Rework the next attempt's instructions when the failure came from framing,
missing constraints, or unclear task decomposition.

Inspect whether the next prompt should:

- add or sharpen success conditions,
- narrow scope,
- emphasize missing evidence requirements,
- remove misleading instructions,
- split one overloaded role into several clearer roles,
- or inject lessons learned from the previous attempt.

Prompt evolution should change the agent's decision boundary, not merely restate
the same request with cosmetic wording.

## Evolution axis 2: Tool evolution

Rework the tool layer when the bottleneck came from missing observability,
repetitive manual operations, weak interfaces, or lack of a specialized helper.

Inspect whether the next attempt should:

- add a new helper tool,
- wrap an existing tool with a better interface,
- synthesize a task-local adapter,
- or explicitly stop using a tool that caused noise or bias.

Tool evolution is appropriate when the task is conceptually understood but the
current tool surface makes execution too brittle or too expensive.

## Evolution axis 3: Workflow evolution

Rework the execution structure when the failure came from sequencing, missing
gates, lack of parallel exploration, or poor role boundaries.

Inspect whether the next attempt should:

- add or remove an intermediate check,
- insert an independent verifier or critic,
- parallelize independent branches,
- switch from one-shot solving to staged solving,
- or simplify an over-engineered plan back into a smaller workflow.

Workflow evolution should change the process graph, not just the wording or the
tool inventory.

## Output of reflection

A useful self-evolution pass should produce a rich next-attempt optimization
record that covers:

- what failure mode or instability was actually observed,
- what to preserve,
- what root-cause hypothesis currently best explains the failure,
- what to change in the prompt,
- what to change in the tool surface,
- what to change in the workflow,
- what diagnostic or stop condition should be checked next,
- and why these changes target the observed failure mode.

Prefer an explicit attempt-to-attempt delta, not a vague motivational note.
The record may live in the next-attempt plan, a structured note, or another
runtime-approved surface.

That delta may live directly in the revised next-attempt prompt or in concise
explanatory notes. If another component imposes extra state-handling
requirements, satisfy them there rather than here.

## Reflection discipline

- Do not blame everything on the prompt. First decide whether the failure was
  about understanding, execution, or process structure.
- Do not change everything at once. Preserve what already worked and alter only
  the boundaries that produced the failure.
- If the root cause is still unclear, make the next round more diagnostic rather
  than blindly more aggressive.
- A pre-registered reminder to reflect later is fine, but do not inject fake
  evolution deltas into the first attempt before any actual trajectory has been
  observed.
- Stop only on judged success or when the configured attempt cap is exhausted.
- When the cap is exhausted without judged success, report the current state
  honestly as incomplete or failed rather than pretending that the last attempt
  passed.
- Reflection may be returned directly in the next-attempt plan or final notes.
  Do not demand a separate reflection sidecar unless another component
  explicitly requires extra state handling.
- The goal of reflection is not to sound wiser. It is to make the next attempt
  repeat fewer known mistakes under the same budget.
