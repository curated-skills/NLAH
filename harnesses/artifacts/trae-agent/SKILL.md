---
name: trae-agent
description: >
  Run a TRAE-style candidate-search harness that treats repository issues as an
  explicit search over independently sampled patch candidates, then prunes,
  selects, and revalidates the strongest one.
---

# TRAE Candidate Search Harness

Treat the reported issue as a repository-level search problem rather than a
single straight-line edit task. In this harness, "search" means repeatedly
sampling full candidate solutions from independent fresh-start attempts, then
running an explicit pruning and selection procedure over those candidates.
It is not enough to stay inside one continuing context and keep revising the
same partial fix while calling each revision a new candidate.
Unless an external budget clearly pins the run to one attempt, do not treat a
single first-pass patch as a faithful TRAE-style execution.

## Search contract

- Candidate generation must use independent contexts. Each candidate attempt
  starts from the same issue statement and the same baseline repository state,
  but from a fresh task context with no carry-over of prior candidates'
  intermediate reasoning, command history, or partial patches.
- A later candidate is not valid if it is just "candidate A after seeing that A
  failed" inside the same continuing trajectory. That is iterative repair, not
  TRAE-style candidate search.
- Cross-candidate comparison is allowed only after a candidate has finished its
  own full attempt. Only then may the harness prune, rank, or select among
  completed candidates.
- If a later batch is needed, the next batch may reuse distilled observations
  from earlier rounds, but each new candidate in that later batch must again be
  generated in a fresh context from the baseline repository state.
- The intended high-level structure is explicit generation, pruning, selection,
  and final revalidation. Do not collapse these stages into a single untracked
  straight-line solve.

## Default search budget

- Match the upstream Trae selector defaults unless an external budget overrides
  them: generate 10 candidates, compare them in groups of 10, and use
  majority-voting selection inside each group.
- Treat majority voting as part of the paper-level default search procedure even
  if a particular implementation exposes it as an optional runtime flag. When
  reproducing the intended Trae behavior, enable that voting loop by default
  rather than inheriting a weaker CLI default that would skip it.
- Treat 10 as the total search budget, not merely the per-batch parallelism. If
  the runtime can launch only a few candidates concurrently, launch them in
  batches until 10 distinct fresh-start candidates have completed or been
  explicitly marked failed/unusable.
- If the total candidate pool is larger than one group, first select one winner
  per group, then run a final selector pass over the group winners using the
  same majority-voting discipline.
- Do not silently shrink the default search to two candidates just because two
  is easier to orchestrate. Any reduction below the default budget must be
  recorded explicitly as a degradation, together with the concrete budget or
  runtime constraint that forced it.
- A vague note such as "practical runtime limits" is not enough. The search
  record must name the concrete overriding constraint, such as a hard user
  budget, fixed wall-clock cap, token cap, or platform failure, and it must
  state the exact executed candidate count.

## Execution flow

1. Clarify the issue text, likely failure mechanism, relevant files, and the
   reproduction path. Use that understanding to plan a small batch of candidate
   attempts rather than committing immediately to a single patch. When no
   tighter budget is supplied, plan the default 10-candidate search rather than
   a minimal two-candidate fallback.
2. Run explicit candidate generation through independent repeated sampling.
   Every candidate must be produced by a fresh attempt that does not inherit the
   running dialogue state of earlier candidates. Variation may come from prompt
   framing, bug hypotheses, decomposition style, verification focus, edit scope,
   or other configuration choices that could lead to meaningfully different
   solutions.
   Label the candidates explicitly, for example `C1` through `C10`, and do not
   begin final selection just because the first few candidates look good.
   Each candidate should still follow the core Trae repair discipline:
   - use absolute paths when invoking file-oriented tools,
   - explore the relevant code and tests before editing,
   - create a reproduction script or test case before changing code,
   - perform structured diagnosis rather than guessing,
   - implement a minimal targeted fix,
   - rerun reproduction and targeted tests before treating that candidate as viable,
   - add a focused regression test for the bug when repository conventions and task scope make that practical.
3. For each candidate, preserve the patch, the reasoning summary, the commands
   used for reproduction or validation, and enough trajectory detail to explain
   how that candidate was produced. Keep candidate boundaries explicit so a
   reviewer can tell where one attempt ends and the next begins.
   Every candidate label must also end with a clear terminal record that marks
   it as `VIABLE`, `FAILED`, or `UNUSABLE` and explains why. Even when a
   candidate dies because of a platform `429`, interruption, or tool failure,
   do not leave that slot as a silent directory or an unclosed hole.
4. Run an explicit pruning stage before final selection. Remove empty, clearly
   broken, duplicate, or weakly evidenced candidates, and keep a shortlist of
   the most credible survivors. When the candidate pool is large, use the
   upstream-style grouped procedure with group size 10 unless an external budget
   overrides it.
   The search should also maintain a structured ledger that states the total
   budget, the actual batching, the outcome of every candidate label, which
   candidates reached the shortlist, and which concrete constraints overrode
   the default budget when a degradation occurred.
5. Compare the shortlisted candidates explicitly. Judge them on issue coverage,
   evidence of correctness, patch minimality, consistency with the repository,
   and residual risk rather than choosing whichever candidate was generated
   first. Produce an explicit ranking before selecting the winner. By default,
   selection should follow majority voting over repeated selector passes instead
   of a single one-shot choice. The selection stage must leave an inspectable
   comparison record and a winner record rather than stopping at a bare list of
   candidate paths.
   Each selector pass should leave its own record stating at least the compared
   candidate set, the ranking or vote result, the elimination rationale, and
   the winner of that pass. If there is grouped selection followed by a final
   round over group winners, both levels must remain separately inspectable.
6. Select the most credible candidate, reapply or reconstruct it if needed, and
   then rerun the issue reproduction steps plus targeted tests in a clean final
   validation pass. Leave an inspectable final-revalidation record that states
   which candidate was accepted, which commands were rerun, and whether the
   winner survived that clean pass.
   That final revalidation record should also point back to the corresponding
   selector result so a reviewer can follow one continuous chain from candidate
   generation through voting to winner acceptance instead of seeing a winner
   appear only inside the final validation note.

## Verification

- Use the same commands that reproduce the bug, along with the most relevant
  targeted tests, to confirm the selected candidate really resolves the issue.
- Require the selected candidate to carry its own evidence trail: reproduction
  script, diagnosis notes, verification commands, and a concise completion
  summary explaining the bug, the fix, and the residual risk.
- If final validation fails, do not force acceptance. Record why the candidate
  failed, identify what evidence was missing, and start another candidate batch
  with improved guidance.
- If the search degenerates to a single candidate because of budget, tool, or
  environment limits, record that degeneration explicitly instead of pretending
  a full candidate search took place.
- If the run uses fewer than 10 candidates, disables majority voting, or skips
  grouped selection when the pool is large, record that deviation explicitly in
  the search record rather than letting it pass as an unmarked default.
- Platform-level failures or interruptions still count as executed candidate
  slots. The search record must preserve those labels together with the failure
  class and concrete cause instead of silently dropping them.
- Do not confuse a concurrency limit with a reduced search budget. Four workers
  may still execute a 10-candidate search by running multiple batches.
- A candidate list alone is not sufficient selection evidence. The run should
  also record how candidates were compared, which candidate won, and why.
- A selected winner without a clean final-revalidation record is still
  incomplete. The run should make it easy to inspect the acceptance check
  separately from candidate generation.
- Do not confuse "multiple edits in one long session" with "multiple sampled
  candidates." The verification record should make it obvious that the accepted
  patch survived a true search over independent candidate attempts.

## Finalization

- Accept the patch only when the selected candidate survives revalidation and
  the search record makes it clear why this candidate beat the alternatives.
- Summarize the winning candidate, the discarded alternatives, and the decisive
  verification evidence so a reviewer can reconstruct the search-and-selection
  process.
