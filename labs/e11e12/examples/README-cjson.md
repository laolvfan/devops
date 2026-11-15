# cJSON real-project profile

The `cjson` profile targets the historical missing `cJSON.h` dependency of
`cJSON_Utils.o` in [cJSON PR #380](https://github.com/DaveGamble/cJSON/pull/380).
It is intentionally limited to this target and runs a fresh GCC dependency
observation on each revision. It does not claim general-purpose Make support.

Use upstream base `359567fdde253f311545a6c80b0fa6fb62e8ff09`, target
`cf0d87a095becada87336ed786f11070e9a037b5`, and compare the generated patch
against upstream fix `20cffa37a8f2d5d4811bb1dbba693c35c0d7f4a6`. The fix is
a reference, not the repair target.

Copy the two Dockerfile examples to `data/` and set request fields
`project_profile=cjson`, `broken_dockerfile`, and `candidate`. These are
an experiment-owned harness for an upstream project which does not carry the
course's `Dockerfile.broken`. DRAFT builds the image and runs cJSON's test
program. Validation runs `make test`, checks that a header change schedules
recompilation, performs the rebuild and rescans for missing dependencies.
The upstream repository and commits remain unchanged.
