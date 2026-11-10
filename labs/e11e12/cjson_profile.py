"""Narrow cJSON Makefile profile for the upstream cJSON_Utils.o dependency."""
import difflib
import re
import subprocess
from pathlib import Path

TARGET = "cJSON_Utils.o"
SOURCE = "cJSON_Utils.c"

def run(argv, cwd):
    result = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=60)
    if result.returncode:
        raise ValueError(f"COMMAND_FAILED {argv!r}: {result.stderr}")
    return result.stdout

def scan(project, old=None):
    project = Path(project)
    database = run(["make", "-np", TARGET], project)
    rules = re.findall(r"^cJSON_Utils\.o:\s*([^\n]*)$", database, re.M)
    if len(rules) != 1:
        raise ValueError("UNSUPPORTED_RULE cJSON_Utils.o")
    declared = sorted(set(rules[0].split()))
    if any(x in declared for x in ("|",)) or any("$" in x for x in declared):
        raise ValueError("UNSUPPORTED_DECLARATION")
    output = run(["gcc", "-MM", "-MT", TARGET, SOURCE], project)
    actual = sorted(set(output.replace("\\\n", " ").split(":", 1)[1].split()))
    findings = [
        {"type": kind, "target": TARGET, "dependency": dependency}
        for kind, deps in (("MISSING", set(actual) - set(declared)),
                           ("REDUNDANT", set(declared) - set(actual)))
        for dependency in sorted(deps)
    ]
    files = {p.name: p.read_text() for p in sorted(project.glob("*")) if p.suffix in {".c", ".h"}}
    key = {"directives": {name: [line for line in text.splitlines() if line.lstrip().startswith("#")]
                          for name, text in files.items()},
           "makefile": (project / "Makefile").read_text(),
           "compiler": run(["gcc", "--version"], project).splitlines()[0]}
    previous = {(f["type"], f["target"], f["dependency"]) for f in old["findings"]} if old else set()
    current = {(f["type"], f["target"], f["dependency"]) for f in findings}
    return {"schema_version": "e8e10-1", "profile": "CJSON_UTILS_EXPLICIT_MAKE",
            "commit": run(["git", "rev-parse", "HEAD"], project).strip(), "key": key,
            "actual": {TARGET: actual}, "declared": {TARGET: declared}, "findings": findings,
            "added": [list(item) for item in sorted(current - previous)],
            "resolved": [list(item) for item in sorted(previous - current)],
            "refreshed": [TARGET], "reused": []}

def patch(project, report):
    project = Path(project)
    if report["commit"] != run(["git", "rev-parse", "HEAD"], project).strip():
        raise ValueError("STALE_REPORT")
    original = (project / "Makefile").read_text()
    changed = original
    edits = []
    for finding in report["findings"]:
        if finding["type"] != "MISSING":
            continue
        target, dependency = finding["target"], finding["dependency"]
        if target != TARGET:
            raise ValueError("UNSUPPORTED_TARGET")
        if not re.fullmatch(r"[\w./-]+", dependency) or ".." in Path(dependency).parts or Path(dependency).is_absolute():
            raise ValueError("UNSAFE_PATH")
        if not (project / dependency).is_file():
            raise ValueError("MISSING_INPUT")
        matches = list(re.finditer(r"^(?:\$\(UTILS_OBJ\)|cJSON_Utils\.o):[ \t]*([^\n]*)$", changed, re.M))
        if len(matches) != 1:
            raise ValueError("UNSUPPORTED_RULE")
        match = matches[0]
        changed = changed[:match.end()] + " " + dependency + changed[match.end():]
        edits.append({"target": target, "dependency": dependency, "style": "variable-target"})
    diff = "".join(difflib.unified_diff(original.splitlines(True), changed.splitlines(True),
                                         fromfile="a/Makefile", tofile="b/Makefile"))
    return diff, edits

def validate(project, patchfile, evidence, fail_test=False):
    import shutil
    project, patchfile, evidence = Path(project), Path(patchfile).resolve(), Path(evidence)
    evidence.mkdir(parents=True)
    before = (project / "Makefile").read_bytes()
    sandbox = evidence / "sandbox"
    shutil.copytree(project, sandbox, ignore=shutil.ignore_patterns(".git", "*.o", "cJSON_test"))
    run(["git", "init", "-q", "-b", "main"], sandbox)
    run(["git", "config", "user.name", "ValidationSandbox"], sandbox)
    run(["git", "config", "user.email", "fixture@localhost"], sandbox)
    run(["git", "add", "."], sandbox)
    run(["git", "commit", "-qm", "sandbox input"], sandbox)
    checks, error = {}, None
    try:
        run(["git", "apply", "--check", str(patchfile)], sandbox)
        run(["git", "apply", str(patchfile)], sandbox)
        checks["patch_applies"] = True
        log = run(["make", "clean"], sandbox) + run(["make", TARGET], sandbox)
        (evidence / "build.log").write_text(log)
        checks["build"] = True
        (evidence / "test.log").write_text(run(["make", "test"], sandbox))
        checks["test"] = not fail_test
        query = subprocess.run(["make", "-q", "-W", "cJSON.h", TARGET],
                               cwd=sandbox, text=True, capture_output=True, timeout=60)
        if query.returncode not in (0, 1):
            raise ValueError("MAKE_QUERY_FAILED " + query.stderr)
        checks["header_change"] = query.returncode == 1
        if checks["header_change"]:
            (evidence / "incremental.log").write_text(run(["make", "-W", "cJSON.h", TARGET], sandbox))
        recheck = scan(sandbox)
        (evidence / "recheck.json").write_text(__import__("json").dumps(recheck, indent=2) + "\n")
        checks["no_missing"] = not any(f["type"] == "MISSING" for f in recheck["findings"])
    except (ValueError, subprocess.TimeoutExpired) as exc:
        error = str(exc)
    accepted = bool(checks) and all(checks.values()) and error is None
    if accepted:
        (project / "Makefile").write_bytes((sandbox / "Makefile").read_bytes())
    unchanged = (project / "Makefile").read_bytes() == before
    result = {"accepted": accepted, "checks": checks, "error": error,
              "source_unchanged": unchanged, "rollback": not accepted and unchanged}
    (evidence / "validation.json").write_text(__import__("json").dumps(result, indent=2) + "\n")
    return result
