# E3 Lab Kit

This repository stores the DevOps course E3 fixtures, instructor-oracle inputs, reference patches, and run evidence. The DRAFT and MDFixer service implementations remain in the separate DevOps project.

## Contents

- `fixtures/draft/`: Tiny Greeting DRAFT fixture is planned; its source and Dockerfiles are not prepared yet. Use `make -C fixtures/draft/tiny-greeting` once that fixture is added.
- `fixtures/mdfixer/missing-header/`: minimal GNU Make project used for the MDFixer missing-header case.
- `oracle/mdfixer/md-report.json`: fixed `INSTRUCTOR_ORACLE` report for the MDFixer baseline.
- `oracle/mdfixer/reference/`: four independent reference patches (Target, Macro, Hybrid, Implicit).
- `evidence/`: captured B2 commands, logs, and observations.
- `work/`: local working copies and build outputs; intentionally excluded from this repository.

## MDFixer source baseline

The `e3-mdfixer-md-v1.0.0` tag preserves the original source-only baseline at commit `4fdc623c51e3fd9c07d4905a9f2bbc8e78d5fa8f`. Checking out this tag places `Makefile`, `main.c`, and `config.h` at the repository root; the package's `main` branch also tracks these files under `fixtures/mdfixer/missing-header/`.

The Oracle report's `repository.url` uses this repository's GitHub URL and its `repository.commit` points to the source-only baseline tag. The four reference patches are alternatives against that tag; apply each to a fresh working copy when running the next validation step.

## Current status

- MDFixer 1B fixed input, B2 stale-output reproduction, and B3 reference patches are prepared.
- Patch application and post-fix behavior validation remain pending.
- DRAFT Tiny Greeting fixture remains pending.

The B2 evidence is in `evidence/20260929T104529-b2/`. It records the baseline build/run, header modification, incremental `make`, stale output, tool versions, and the source tag/commit.