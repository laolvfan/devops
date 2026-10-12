# E3 MDFixer missing-header fixture

This is a course test fixture for B Group E3. `main.c` includes `config.h`, while the baseline `main.o` rule in `Makefile` intentionally lists only `main.c`.

## Baseline

- `config.h` defines `VALUE` as `1`.
- The fixed instructor-oracle report is stored outside this source repository at `../../../oracle/mdfixer/md-report.json`.
- The report uses the new E3 Lab Kit GitHub repository URL and points to the immutable source-only baseline tag. It describes the expected finding `main.o -> config.h`.
- The report producer ID is synthetic fixture metadata required by the shared E2 schema; no detector Job has run.

## Commands for the later 2B behavior check

Run these commands only in a fresh working copy of the tagged baseline:

```sh
make clean && make
./app
```

The initial program should print `1`. Change `VALUE` to `2` in `config.h`, run `make` without `clean`, and observe whether the output remains stale. Record actual output and exit codes under the run's evidence directory; this README describes expected behavior, not a completed run.