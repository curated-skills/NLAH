# Module Authoring

## Scope

LinguaClaw distinguishes between three kinds of natural-language artifacts:

- `runtime-policy/`
  - the always-on interpreter policy.
- `harnesses/modules/`
  - reusable modules loaded fully into context with `--harness`.
- `harnesses/artifacts/`
  - larger harness bundles and imported reference behaviors.

`tool-skills/` are intentionally different.
They are peripheral helpers and should follow progressive disclosure instead of unconditional full loading.

## Module Rules

1. Keep modules English-only.
2. Keep one `SKILL.md` per module directory.
3. Prefer concrete behavioral contracts over generic advice.
4. Assume a bash-first runtime with minimal persistent state.
5. Make any required files, artifacts, or stopping conditions explicit.
6. Do not silently depend on hidden runtime features.

## Naming

- Use kebab-case directory names.
- Imported `*-module` assets should drop the `-module` suffix in LinguaClaw.

Examples:

- `harnesses/modules/file-backed-state/SKILL.md`
- `harnesses/modules/verifier/SKILL.md`
- `tool-skills/github-cli/SKILL.md`

## Recommended Frontmatter

Imported seed materials already use a lightweight frontmatter style.
New public modules should stay close to that pattern.

```yaml
---
name: file-backed-state
description: >
  Persist only the extra state your harness truly needs beyond the built-in
  run parameters and message history.
---
```

## Authoring Guidance

- A module should say what it is for, when it should be loaded, and what it changes.
- If it requires a state file, artifact layout, or handoff surface, name that path explicitly.
- If it assumes a special capability beyond bash, say so directly.
- If the artifact really represents a whole end-to-end harness rather than a reusable pattern, place it under `harnesses/artifacts/` instead.

## Tool Skills

Keep `tool-skills/` thin.
They should wrap optional external capabilities such as GitHub-side inspection and should not duplicate the core runtime policy.
