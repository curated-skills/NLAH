# Natural-Language Agent Harnesses

[![arXiv](https://img.shields.io/badge/arXiv-2603.25723-b31b1b.svg)](https://arxiv.org/abs/2603.25723)
[![CI](https://github.com/curated-skills/NLAH/actions/workflows/ci.yml/badge.svg)](https://github.com/curated-skills/NLAH/actions/workflows/ci.yml)
[![Release](https://github.com/curated-skills/NLAH/actions/workflows/release.yml/badge.svg)](https://github.com/curated-skills/NLAH/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A next-generation agent harness, implemented mainly in natural language, to unlock the full potential of LLMs. You can customize your own harness with minimal code.

This repository is the official open-source home of the **Natural-Language Agent Harnesses (NLAH)** project.
The paper argues that harness logic should be made explicit, editable, and executable as natural-language artifacts instead of being buried in framework-specific controller code.

Paper: [Natural-Language Agent Harnesses](https://arxiv.org/abs/2603.25723)

## What We Are Open-Sourcing

The broader NLAH open-source effort is organized around three connected layers:

1. The runtime itself together with reusable natural-language harnesses.
2. An experiment platform for testing agents and skills on benchmarks.
3. A unified interface for running dozens of agents under one consistent contract.

This repository is the public starting point for that effort.
The benchmark-facing experiment platform will live in a separate repository; this repository focuses on the runtime, reusable harnesses, and the public package surface.

## Why NLAH

Modern agent performance increasingly depends on harness engineering, but harness logic is often hidden inside glue code, runtime defaults, and framework-specific orchestration.
NLAH treats harness design as a first-class artifact:

- Natural-language-first harness logic instead of hard-coded controller bundles.
- Explicit contracts, roles, artifacts, and stopping conditions.
- A shared runtime that can interpret reusable harness modules.
- A path toward more modular benchmarking, comparison, and customization.

In practice, we care about harnesses that can coordinate subagents, memory, compression, verification, and task-specific procedures without freezing every decision into handwritten controller code.

## Current Status

This public repository is in the initial bootstrap phase.
We are setting up the packaging, documentation, and release process first, then rolling out the runtime, harness modules, and benchmark-facing components in stages.

## Repository Layout

- `src/nlah/`: the Python package for the public NLAH runtime scaffold.
- `.github/workflows/`: CI and release automation.
- `CONTRIBUTING.md`: contribution guidelines for open collaboration.

## Getting Started

```bash
uv tool install git+https://github.com/curated-skills/NLAH.git
nlah --version
```

For local development, clone the repository and install it in editable mode:

```bash
git clone https://github.com/curated-skills/NLAH.git
cd NLAH
uv venv
source .venv/bin/activate
uv pip install -e .[dev]
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

This project is intentionally friendly to natural-language-first development.
Traditional unit tests are welcome when they fit, but behavior reports, demo artifacts, and trajectory-based evidence are often more informative for harness changes.

## Acknowledgements

Special thanks to [Ronak Shah](https://x.com/rronak_/status/2038401494177694074) for the public signal boost and the broader discussion around harness engineering that helped motivate this project.
