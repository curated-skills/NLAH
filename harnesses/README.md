# Harnesses

This directory contains the natural-language artifacts that shape runtime behavior.

## Layout

- `modules/`
  - reusable full-load harness modules that can be selected explicitly with `--harness`.
- `artifacts/`
  - larger harness bundles and imported reference agents preserved as artifact-style behaviors.

In practice, `--harness` usually points at one of the artifact directories here.
If you want a lighter composition, it can also point at one or more entries under `modules/`.

## Current State

The first imported files in this directory were copied from the internal research prototype.
They are seed materials for the public repository.
Some of them will be normalized over time so they better match the public bash-first runtime contract.
