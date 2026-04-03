# Contributing

Thanks for contributing to LinguaClaw.
This project sits at the intersection of runtime engineering, natural-language harness design, and benchmark-oriented agent evaluation, so we optimize for changes that are explicit, scoped, and easy to review.

## What We Welcome

- Runtime improvements and harness execution infrastructure.
- Reusable natural-language harness modules and patterns.
- Unified-agent interface work.
- Documentation and release-engineering improvements.

## Before You Open A Pull Request

- Read [README.md](README.md) for the public project overview.
- Keep each pull request focused on one main concern.
- If the change is large or architectural, open an issue or discussion first.

## Development Setup

```bash
uv venv
source .venv/bin/activate
uv pip install -e .[dev]
```

Useful local checks:

```bash
linguaclaw --version
python -m build --outdir dist
python -m twine check dist/*
```

## Natural-Language-First Contributions

Many important changes in this project affect behavior through prompts, harness logic, contracts, artifact structure, or agent coordination rather than through traditional unit-test surfaces.
Because of that, a pull request is **not required** to include automated tests in every case.

If your change mainly affects behavior, include a short behavior report in the pull request description.
Good reports usually include:

- The task or scenario you changed.
- The expected behavioral difference.
- A concise artifact, transcript, or trajectory summary.
- Known risks, regressions, or open validation gaps.

If a practical automated test clearly fits the change, adding it is still encouraged.

## Style Expectations

- Prefer clear, direct technical writing.
- Keep behavior contracts explicit.
- Avoid oversized pull requests with mixed concerns.
- Do not bury major behavior changes inside unrelated formatting churn.

## Release Expectations

If you touch packaging, release automation, or versioning:

- Make sure the version in `pyproject.toml` is correct.
- Verify that `python -m build` succeeds.
- Verify that `python -m twine check dist/*` succeeds.
- Keep release changes small and easy to audit.
