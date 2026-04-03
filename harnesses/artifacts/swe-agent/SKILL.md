---
name: swe-agent
description: Resolve repository issues by reproducing failures, editing source, verifying the fix, and producing a git patch that serves as the experiment's primary artifact.
---

# SWE-Agent

This skill distills the SWE-agent workflow: understand the bug, reproduce it with a scripted command, craft a minimal patch, and prove the fix through the relevant tests.

## Primary Constraints

- Keep the working copy in place and operate through the provided structured editor surface plus the available shell helpers. When a `str_replace_editor`-style tool is available, prefer it for localized edits.
- Keep lightweight notes or summaries only as needed to preserve the reproduction path, verification commands, and any unresolved risk; do not invent heavyweight bookkeeping that is not helping the fix.
- Summaries should highlight how the reproduced failure maps to the proposed patch and which verification commands confirm its resolution.
- Preserve the original SWE-agent posture: understand the bug first, script the reproduction, make the smallest credible fix, and verify it with targeted commands.
- Keep the change set focused on non-test source files and avoid weakening existing tests. Treat test edits as exceptional and justify them explicitly if they become unavoidable.
- If tests are touched, the final handoff must say why a source-only fix or
  source-only verification was insufficient.
- Prefer a file-backed reproduction script that can be rerun as `python <filename.py>` or the nearest repo-native equivalent, rather than relying only on transient heredoc commands.

## Stage 1 — Prepare the environment

1. Read the issue description carefully and turn it into a concrete hypothesis about the failure mode, affected files, and expected behavior.
2. Confirm the available editing, search, and execution tools are working; prefer the simplest reliable helper for reproduction and patch synthesis.
3. If the provided editor or file viewer elides large bodies, switch to targeted navigation with `grep -n`, focused views, or other repo-native search commands rather than forcing full dumps.

## Stage 2 — Understand and reproduce

1. Turn the issue description into a focused hypothesis: enumerate the failing files, the expected behavior, and any relevant logs or stack traces.
2. Explore the repository to identify the modules under test; keep a short checklist so you can note which files you touched and why.
3. Build a concise reproduction script file and keep rerunning that file until the failure manifests. Save both the script path and its output for downstream verification.
4. If the failure does not reproduce, iterate on the reproduction assumption rather than blindly re-running the same command.

## Stage 3 — Fix and verify

1. After reproduction succeeds, craft the smallest patch that fixes the root cause. Use the structured editor surface to keep edits localized, and keep the rationale for each edit short and concrete.
2. Execute the verification command(s) that directly cover the failure (the same ones you used to reproduce it, plus any adjacent smoke tests). Record each command and its success/failure status for later traceability.
3. If a verification command still fails, update your hypothesis and plan the next edit or command from the failure evidence instead of broadening the patch blindly.

## Stage 4 — Reflection and retry

1. After any rejection, capture the failing commands, their outputs, and the suspected revision points. Use those clues to adjust the next edit rather than re-running the same workflow.
2. Keep attempts conceptually isolated so you can compare hypotheses and avoid silently carrying over a broken plan.
3. Resist rerunning identical commands in the same attempt; when you do rerun something, explain what changed in your expectation.

## Stage 5 — Finalization

1. Before treating the fix as done, rerun the latest reproduction command if any code changed after the previous verification pass.
2. Remove temporary reproduction scripts when they are no longer needed for handoff.
3. Run a final self-review pass before handoff: inspect the diff, confirm no accidental or nonessential test edits remain, and revert any such edits.
4. If the runtime provides a submit-style handoff or review gate, use it as the authoritative finalization path. Expect the first submission to potentially return a review checklist, address it, and then resubmit.
5. If no submit-style surface exists in the current runtime, emulate the same discipline explicitly: inspect the diff, remove temporary repro files, and only then export the final patch artifact.
6. Describe the outstanding risks (if any) and the next follow-up steps so reviewers can judge the remaining uncertainty.

## Response expectations

Always close the skill with a sentence that recaps the reproduction command, the patch rationale, and the verification commands. Spell out any remaining risks.
