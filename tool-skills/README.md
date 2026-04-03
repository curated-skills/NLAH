# Tool Skills

This directory is reserved for peripheral skills that should not be pinned into the main prompt by default.

Typical examples include:

- GitHub CLI helpers,
- repository metadata lookups,
- external service wrappers,
- and other environment-specific utilities.

Unlike `harnesses/modules/`, these skills should follow progressive disclosure:

- load metadata first,
- load the full body only when the runtime or operator decides the skill is actually needed.

The initial public repository starts with one thin example skill:

- `github-cli/`
  - a seed progressive-disclosure skill for GitHub-side inspection tasks.

The directory exists now so the architectural boundary is explicit from the start.
