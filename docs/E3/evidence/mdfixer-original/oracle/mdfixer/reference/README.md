# MDFixer reference patches

- Baseline tag: e3-mdfixer-md-v1.0.0
- Baseline commit: 4fdc623c51e3fd9c07d4905a9f2bbc8e78d5fa8f
- Prepared: 2026-09-29T11:02:57+08:00

Each file is an independent expected answer against the same frozen Makefile. Apply one patch to a fresh working copy of the baseline; do not stack these alternatives on one another. The patches are not part of the source baseline repository.

| Patch | Declaration style | Expected Makefile change |
|---|---|---|
| target.patch | Target | Add config.h directly to main.o prerequisites. |
| macro.patch | Macro | Add config.h to DEPS and make main.o depend on DEPS. |
| hybrid.patch | Hybrid | Keep main.c explicit and add the HEADERS macro containing config.h. |
| implicit.patch | Implicit | Use a %.o: %.c rule, generate and include main.d with GCC -MMD -MP, and remove the .d file on clean. |

These are reference patches for 3B. All four passed a read-only `git apply --check` against the B2 working copy. Applying each patch, building, and validating the later header-change rebuild remain for the next step.
