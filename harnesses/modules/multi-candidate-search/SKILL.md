---
name: multi-candidate-search-module
description: >
  Make multi-candidate search explicit: allocate a search budget, diversify
  candidate generation, prune weak branches, and select the strongest remaining
  candidate.
---

# Multi-Candidate Search Module

Load this module when one attempt is too brittle and the task benefits from
searching several alternative candidates before committing to one.

## When to use

Use multi-candidate search when:

- the solution space is ambiguous,
- local optima are common,
- different hypotheses may all look plausible at first,
- or the task is important enough that one-shot solving is too fragile.

## Search budget

- Choose an explicit candidate budget `K`.
- If the user or task does not specify `K`, default to `K=5`.
- Start with that meaningful default budget, then expand only if the surviving
  candidates remain inconclusive.
- Respect any user-specified budget or limit before adding more branches.
- If a branch fails before it returns comparable evidence, that slot does not
  count toward the explored budget. Relaunch a replacement branch or state
  explicitly that the search finished with a reduced effective budget.

## Search modes

- For short-form reasoning tasks, a self-consistency style search can be enough:
  sample several genuinely different candidates, then compare or vote among the
  survivors.
- For compositional tasks, use a tree-style search only if you also have an
  explicit evaluation signal for partial branches, such as tests, constraint
  checks, or a clear value function.
- Stop early when one candidate is decisively ahead on task-fit and evidence
  quality; more branches are not automatically better.

## Diversity policy

Candidates should not be trivial rewrites of one another.
Deliberately vary at least one of the following:

- core hypothesis,
- decomposition strategy,
- evidence route,
- tool usage plan,
- or risk preference.

The goal is to cover distinct plausible solution modes rather than sample near
duplicates.

## Pruning policy

Before final selection, remove candidates that are:

- duplicates,
- internally inconsistent,
- unsupported by evidence,
- obviously dominated by a stronger candidate,
- or too risky relative to task requirements.

Pruning should be lightweight early and stricter later.

## Selection policy

Among the surviving candidates, prefer the one that best satisfies the task
while minimizing residual risk.
Selection should consider:

- task-fit,
- evidence quality,
- internal coherence,
- robustness to likely edge cases,
- and cost of downstream repair if it turns out to be wrong.
- When absolute scoring is noisy, prefer pairwise comparison between surviving
  candidates over isolated scalar ratings.
- Do not reward verbosity by default. Longer candidates should win only when
  they carry proportionally stronger evidence or coverage.

## Escalation policy

If no candidate is good enough, do not force a winner.
Instead:

- expand the search budget,
- change the diversification axes,
- or trigger a new round with refined guidance.
- Treat rate limits, infrastructure failures, and branch crashes that prevent a
  branch from returning evidence as missing-budget events rather than as normal
  pruning outcomes.
- If infrastructure noise or branch failure prevents a real comparison, treat the
  search as incomplete unless you actually restore the missing search budget in a
  later round. Do not silently collapse to one surviving worker and still call
  the result a normal multi-candidate success.

## Search discipline

- Candidate count is not the goal. The goal is to cover meaningfully different
  plausible approaches within a finite budget.
- Do not mistake small wording changes for genuine diversity.
- When one candidate is clearly dominated by another, prune it early and spend
  the budget on branches with higher information value.
- If no candidate reaches acceptable quality, explicitly accept that the search
  failed rather than submitting a known-fragile winner.
- Make branch generation, pruning, and selection visible in behavior or final
  explanation, but do not create special search sidecars unless another loaded
  component requires them.
- If branch-level comparison surfaces are truly needed, keep only the minimum
  comparison surface instead of exporting whole branch worktrees by default.
- By default, avoid ad hoc search sidecars or scoreboards. Parent commentary,
  child returns, and the final explanation are the normal audit surface unless
  another loaded component explicitly requires additional state handling.
