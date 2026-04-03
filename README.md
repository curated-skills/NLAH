# LinguaClaw

[![arXiv](https://img.shields.io/badge/arXiv-2603.25723-b31b1b.svg)](https://arxiv.org/abs/2603.25723)
[![CI](https://github.com/curated-skills/NLAH/actions/workflows/ci.yml/badge.svg)](https://github.com/curated-skills/NLAH/actions/workflows/ci.yml)
[![Release](https://github.com/curated-skills/NLAH/actions/workflows/release.yml/badge.svg)](https://github.com/curated-skills/NLAH/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A Claude-Code-style agent harness implemented mostly in natural language: LiteLLM at the model boundary, one bash tool at the action boundary, and reusable harness modules everywhere else.

LinguaClaw is the open-source implementation and continuation of the **Natural-Language Agent Harnesses (NLAH)** line of work.
We are building it as a natural-language implementation of the Claude Code idea: a very thin runtime, a strong runtime policy, and most behavior expressed as reusable markdown modules instead of framework glue code.

Paper: [Natural-Language Agent Harnesses](https://arxiv.org/abs/2603.25723)
Reproduction guide (WIP): [How to Reproduce the NLAH Paper Results](https://github.com/curated-skills/NLAH/wiki/How-to-Reproduce-the-NLAH-Paper-Results)

## What We Are Open-Sourcing

The broader LinguaClaw open-source effort is organized around three connected layers:

1. The runtime itself together with reusable natural-language harnesses.
2. An experiment platform for testing agents and skills on benchmarks.
3. A unified interface for running dozens of agents under one consistent contract.

This repository is the public starting point for that effort.
The benchmark-facing experiment platform will live in a separate repository; this repository focuses on the runtime, reusable harnesses, and the public package surface.

## Why LinguaClaw

Modern agent performance increasingly depends on harness engineering, but harness logic is often hidden inside glue code, runtime defaults, and framework-specific orchestration.
LinguaClaw treats harness design as a first-class artifact:

- Natural-language-first harness logic instead of hard-coded controller bundles.
- Explicit contracts, roles, artifacts, and stopping conditions.
- A shared runtime that can interpret reusable harness modules.
- A path toward more modular benchmarking, comparison, and customization.

In practice, we care about harnesses that can coordinate subagents, memory, compression, verification, and task-specific procedures without freezing every decision into handwritten controller code.

## Current Status

This public repository is in the architecture-freeze and structure-bootstrap phase.
The runtime code will stay intentionally small.
We are first organizing the runtime policy, imported seed modules, public docs, and package layout, then implementing the minimal appserver loop on top of that structure.

## Repository Layout

- `src/linguaclaw.py`: the thin public entry module for the runtime CLI.
- `src/appserver/`: the planned runtime core that will assemble prompts, call LiteLLM, execute tools, and emit a JSONL event stream.
- `src/rich_cli/`: the planned human-facing Rich CLI that will render the appserver event stream.
- `runtime-policy/SKILL.md`: the standing runtime policy and interpreter charter.
- `harnesses/modules/`: reusable full-load harness modules.
- `harnesses/artifacts/`: imported artifact-style harnesses and reference agent behaviors.
- `tool-skills/`: peripheral tool-oriented skills that should be loaded progressively instead of being pinned into the main prompt by default.
- `docs/architecture.md`: the architectural specification for the public runtime.
- `docs/module-authoring.md`: module and skill authoring rules.
- `docs/roadmap.md`: the staged roadmap for runtime, multimodality, CLI, sandboxing, and ecosystem support.
- `.github/workflows/`: CI and release automation.

## Getting Started

```bash
uv tool install git+https://github.com/curated-skills/NLAH.git
linguaclaw --version
```

For local development, clone the repository and install it in editable mode:

```bash
git clone https://github.com/curated-skills/NLAH.git
cd LinguaClaw
uv venv
source .venv/bin/activate
uv pip install -e .[dev]
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

This project is intentionally friendly to natural-language-first development.
Traditional unit tests are welcome when they fit, but behavior reports, demo artifacts, and trajectory-based evidence are often more informative for harness changes.

## Architecture And Roadmap

- Architecture: [docs/architecture.md](docs/architecture.md)
- Module authoring: [docs/module-authoring.md](docs/module-authoring.md)
- Roadmap: [docs/roadmap.md](docs/roadmap.md)

The short version is simple:
this repository will ship a thin runtime built around `LiteLLM + one bash tool + file-backed state + reusable markdown harness modules`.
Benchmark orchestration and large-scale experiment plumbing will stay in a separate repository.

## Acknowledgements

Special thanks to [Ronak Shah](https://x.com/rronak_/status/2038401494177694074) for the public signal boost and the broader discussion around harness engineering that helped motivate this project.
