#!/usr/bin/env bash
set -u

RUN_ID="20260929T104529-b2"
PKG="$HOME/e3-lab-kit"
SRC="$PKG"
WORK="$PKG/work/$RUN_ID/mdfixer"
EVID="$PKG/evidence/$RUN_ID"
TAG="e3-mdfixer-md-v1.0.0"

mkdir -p "$PKG/work/$RUN_ID" "$EVID"
if [ -e "$WORK/.git" ]; then
  echo "Refusing to reuse an existing work copy: $WORK" >&2
  exit 2
fi

git clone --quiet --no-local --branch "$TAG" "$SRC" "$WORK"
cd "$WORK" || exit 2
SOURCE_SHA="$(git rev-parse HEAD)"
INITIAL_STATE="$(git status --porcelain)"
INITIAL_VALUE="$(awk '/^#define VALUE / {print $3}' config.h)"
printf 'run_id=%s\ntag=%s\nsource_commit=%s\ninitial_value=%s\n' \
  "$RUN_ID" "$TAG" "$SOURCE_SHA" "$INITIAL_VALUE" > "$EVID/source.txt"

printf 'command: make clean\ncommand: make\n' > "$EVID/01-baseline-build.log"
make clean >> "$EVID/01-baseline-build.log" 2>&1
CLEAN_RC=$?
make >> "$EVID/01-baseline-build.log" 2>&1
BASELINE_BUILD_RC=$?

printf 'command: ./app\n' > "$EVID/02-baseline-run.log"
./app >> "$EVID/02-baseline-run.log" 2>&1
BASELINE_RUN_RC=$?

printf 'command: sleep 2\ncommand: sed -i ... config.h\n' > "$EVID/03-header-change.log"
sleep 2
sed -i 's/^#define VALUE 1$/#define VALUE 2/' config.h
EDIT_RC=$?
CHANGED_VALUE="$(awk '/^#define VALUE / {print $3}' config.h)"
HEADER_MTIME="$(stat -c '%y' config.h)"
OBJECT_MTIME_BEFORE="$(stat -c '%y' main.o)"
HEADER_EPOCH="$(stat -c '%Y' config.h)"
OBJECT_EPOCH_BEFORE="$(stat -c '%Y' main.o)"
printf 'edit_exit_code=%s\nconfig_value=%s\nconfig.h_mtime=%s\nmain.o_mtime_before_make=%s\n' \
  "$EDIT_RC" "$CHANGED_VALUE" "$HEADER_MTIME" "$OBJECT_MTIME_BEFORE" >> "$EVID/03-header-change.log"

printf 'command: make (without clean)\n' > "$EVID/04-incremental-make.log"
make >> "$EVID/04-incremental-make.log" 2>&1
INCREMENTAL_MAKE_RC=$?
OBJECT_MTIME_AFTER="$(stat -c '%y' main.o)"
OBJECT_EPOCH_AFTER="$(stat -c '%Y' main.o)"
printf 'main.o_mtime_after_make=%s\n' "$OBJECT_MTIME_AFTER" >> "$EVID/04-incremental-make.log"

printf 'command: ./app\n' > "$EVID/05-incremental-run.log"
./app >> "$EVID/05-incremental-run.log" 2>&1
INCREMENTAL_RUN_RC=$?

FINAL_VALUE="$(awk '/^#define VALUE / {print $3}' config.h)"
FINAL_STATE="$(git status --porcelain)"
PLATFORM="$(uname -m)"
OS_RELEASE="$(. /etc/os-release && echo "$PRETTY_NAME")"
GCC_VERSION="$(gcc --version | head -n 1)"
MAKE_VERSION="$(make --version | head -n 1)"
export RUN_ID TAG SOURCE_SHA INITIAL_STATE INITIAL_VALUE CLEAN_RC BASELINE_BUILD_RC BASELINE_RUN_RC
export EDIT_RC CHANGED_VALUE HEADER_MTIME OBJECT_MTIME_BEFORE OBJECT_MTIME_AFTER HEADER_EPOCH OBJECT_EPOCH_BEFORE OBJECT_EPOCH_AFTER
export INCREMENTAL_MAKE_RC INCREMENTAL_RUN_RC FINAL_VALUE FINAL_STATE PLATFORM OS_RELEASE GCC_VERSION MAKE_VERSION

python3 - "$EVID" <<'PY'
import json
import os
import sys
from pathlib import Path

evidence = Path(sys.argv[1])

def log(name):
    return (evidence / name).read_text(encoding="utf-8")

def output(name):
    lines = [line for line in log(name).splitlines() if not line.startswith(("command:", "commands:", "main.o_mtime_"))]
    return "\n".join(lines).strip()

commands = {
    "run_id": os.environ["RUN_ID"],
    "source_tag": os.environ["TAG"],
    "source_commit": os.environ["SOURCE_SHA"],
    "steps": [
        {"step": "baseline_build", "commands": ["make clean", "make"], "clean_exit_code": int(os.environ["CLEAN_RC"]), "build_exit_code": int(os.environ["BASELINE_BUILD_RC"]), "log": "01-baseline-build.log"},
        {"step": "baseline_run", "command": "./app", "exit_code": int(os.environ["BASELINE_RUN_RC"]), "expected_stdout": "1", "log": "02-baseline-run.log"},
        {"step": "change_header", "commands": ["sleep 2", "sed -i 's/^#define VALUE 1$/#define VALUE 2/' config.h"], "exit_code": int(os.environ["EDIT_RC"]), "log": "03-header-change.log"},
        {"step": "incremental_make", "command": "make", "clean_before_run": False, "exit_code": int(os.environ["INCREMENTAL_MAKE_RC"]), "log": "04-incremental-make.log"},
        {"step": "incremental_run", "command": "./app", "exit_code": int(os.environ["INCREMENTAL_RUN_RC"]), "expected_stale_stdout": "1", "log": "05-incremental-run.log"},
    ],
}
observations = {
    "run_id": os.environ["RUN_ID"],
    "source_tag": os.environ["TAG"],
    "source_commit": os.environ["SOURCE_SHA"],
    "initial_worktree_status": os.environ["INITIAL_STATE"],
    "worktree_status_after_run": os.environ["FINAL_STATE"],
    "environment": {"os": os.environ["OS_RELEASE"], "platform": os.environ["PLATFORM"], "gcc": os.environ["GCC_VERSION"], "make": os.environ["MAKE_VERSION"], "configuration_id": "cfg-ubuntu24-gcc13-debug-v1"},
    "baseline": {"config_value": int(os.environ["INITIAL_VALUE"]), "build_exit_code": int(os.environ["BASELINE_BUILD_RC"]), "run_exit_code": int(os.environ["BASELINE_RUN_RC"]), "stdout": output("02-baseline-run.log")},
    "after_header_change": {"config_value": int(os.environ["CHANGED_VALUE"]), "header_mtime": os.environ["HEADER_MTIME"], "main_o_mtime_before_make": os.environ["OBJECT_MTIME_BEFORE"], "main_o_mtime_after_make": os.environ["OBJECT_MTIME_AFTER"], "header_newer_than_object": int(os.environ["HEADER_EPOCH"]) > int(os.environ["OBJECT_EPOCH_BEFORE"])},
    "incremental": {"make_exit_code": int(os.environ["INCREMENTAL_MAKE_RC"]), "make_log": "04-incremental-make.log", "run_exit_code": int(os.environ["INCREMENTAL_RUN_RC"]), "stdout": output("05-incremental-run.log"), "stale_output_reproduced": int(os.environ["CHANGED_VALUE"]) == 2 and output("05-incremental-run.log") == "1"},
}
(evidence / "commands.json").write_text(json.dumps(commands, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(evidence / "observations.json").write_text(json.dumps(observations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

cp "$0" "$EVID/run_b2.sh"
echo "RUN_ID=$RUN_ID"
echo "SOURCE_TAG=$TAG"
echo "SOURCE_SHA=$SOURCE_SHA"
echo "BASELINE_BUILD_RC=$BASELINE_BUILD_RC BASELINE_RUN_RC=$BASELINE_RUN_RC"
echo "HEADER_VALUE_AFTER_EDIT=$CHANGED_VALUE HEADER_MTIME=$HEADER_MTIME OBJECT_MTIME=$OBJECT_MTIME_BEFORE"
echo "INCREMENTAL_MAKE_RC=$INCREMENTAL_MAKE_RC OBJECT_MTIME_AFTER=$OBJECT_MTIME_AFTER INCREMENTAL_RUN_RC=$INCREMENTAL_RUN_RC"
echo "EVIDENCE=$EVID"
