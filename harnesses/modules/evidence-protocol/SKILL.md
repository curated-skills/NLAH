---
name: evidence-protocol-module
description: Require a standalone, citation-backed evidence document and gate final answer release on its completeness.
---

# Evidence Protocol Module

Load this module whenever the solving stage must produce a detailed,
citation-backed analysis before any final answer is released.
This module owns the analysis discipline: what the evidence document must
contain, how claims must be cited, and when the answer may be released.
It is not the verifier role.

## Required evidence document

- Before releasing the final answer, write one standalone evidence document.
  If the task gives a path, use it. Otherwise default to `analysis.md` inside
  the current stage's artifact directory.
- That evidence document is mandatory. A final answer, final patch, or final
  "solved" claim is not releasable until the document exists and is materially
  complete.
- The final answer may summarize the document, but it must not replace it.
- This module deliberately requires a standalone evidence artifact rather than
  scattering all justification only across transient chat replies.

## Required document structure

The evidence document should contain the following sections whenever they are
applicable:

1. Problem statement and the candidate resolution being argued for.
2. Relevant components, files, functions, tests, or external materials that
   materially participate in the issue.
3. Observed failure symptoms, reproduction results, or other direct motivating
   signals.
4. Root cause and the full causal chain from defect to observed behavior.
5. Candidate changes or proposed answer, mapped claim-by-claim to the evidence.
6. Validation results after the change, including what was checked and what was
   not.
7. Residual uncertainty, open questions, and unsupported hypotheses.

## Claim discipline

Every important claim in that document should make clear:

- what the claim is,
- what original observation, test result, command output, quoted content, or
  external source it comes from,
- what minimal supporting span, excerpt, or concrete output segment best anchors
  that claim when such a span exists,
- whether the claim is a direct observation or an inference from observations,
- what intermediate reasoning connects the source to the claim when inference is
  involved,
- and what uncertainty remains unresolved.

## Citation and provenance discipline

- When citing command outputs, test results, captured content, or external
  materials,
  identify the source precisely enough that a reviewer can tell where the claim
  came from.
- For repository claims, prefer direct file links with precise line anchors,
  such as `[server.py](/abs/path/to/server.py#L120)`.
- For command outputs or tests, identify the command, the produced artifact or
  log path when available, and the observation time when timing matters.
- For time-sensitive external sources, state the observation time as part of the
  provenance.
- Separate raw facts from your interpretation of those facts. Do not disguise an
  interpretation as if it were directly observed.
- When a conclusion depends on multiple sources, say which part of the claim
  each source supports instead of dumping a source list without attribution.
- Before releasing an important conclusion, break it into claim-scoped
  verification questions that can be answered independently of the draft's own
  wording.
- If the evidence is incomplete, do not present the statement as settled fact.
  Mark it as a hypothesis, suspicion, or open question.
- If a source supports only part of a stronger claim, release only the supported
  part instead of silently inflating the conclusion.

## Answer gated release

- Before declaring the problem solved, check whether every release-critical
  claim is backed by adequate citations inside the evidence document.
- If any critical gap, uncited claim, broken reasoning chain, or unresolved
  contradiction remains, do not release the answer as fully complete.
- The final answer should clearly separate what is fully supported from what
  remains partial or open, and it should point back to the evidence document as
  the detailed basis.
- Producing this document is the responsibility of the current solving or
  analysis stage. A later verifier may consume it, but the verifier does not
  replace it.

The goal of this protocol is that every major conclusion can survive the
question "why are you allowed to say that?" with a precise and reviewable
answer.
