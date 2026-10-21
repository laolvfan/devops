import hashlib
import json
from pathlib import Path

import pytest

from scripts.verify_e6_b_evidence import verify


def make_evidence(root: Path, *, replay=True):
    evidence = root / "evidence"
    (evidence / "iter-01").mkdir(parents=True)
    (evidence / "iter-02").mkdir()
    project = evidence / "project"
    project.mkdir()
    dockerfile = b"FROM pinned-image\nRUN make\n"
    (evidence / "iter-02" / "Dockerfile").write_bytes(dockerfile)
    (evidence / "iter-01" / "build-stdout.log").write_text("", encoding="utf-8")
    (evidence / "iter-01" / "build-stderr.log").write_text("/bin/sh: 1: make: not found\n", encoding="utf-8")
    image = "sha256:" + "a" * 64
    (evidence / "iter-02" / "image-inspect.json").write_text(json.dumps([{"Id": image}]), encoding="utf-8")
    (evidence / "verify.log").write_text("hello E3\n", encoding="utf-8")
    source = b"int main(void) { return 0; }\n"
    (project / "main.c").write_bytes(source)
    candidate_sha = hashlib.sha256(dockerfile).hexdigest()
    candidate_source = "teaching-replay" if replay else "student-candidate"
    (root / "invocation.json").write_text(json.dumps({
        "stage": "e6", "replay": replay, "candidate_sha256": candidate_sha,
        "candidate_source": candidate_source,
    }), encoding="utf-8")
    report = {
        "status": "SUCCEEDED", "trace_id": "e6-b-test", "candidate_sha256": candidate_sha,
        "candidate_source": candidate_source,
        "attempts": [
            {"iteration": 1, "build_exit_code": 1, "failure_class": "MISSING_MAKE"},
            {"iteration": 2, "build_exit_code": 0, "image_id": image},
        ],
        "verification": {
            "command": ["docker", "run", image], "exit_code": 0,
            "output_matches": True, "actual_output": "hello E3\n", "expected_output": "hello E3",
        },
        "input_sha256": {"main.c": hashlib.sha256(source).hexdigest()},
    }
    (evidence / "result.json").write_text(json.dumps(report), encoding="utf-8")
    return evidence


def test_verifier_reports_candidate_source_and_replay(tmp_path):
    result = verify(make_evidence(tmp_path))
    assert result["passed"] is True
    assert result["candidate_source"] == "teaching-replay"
    assert result["replay"] is True


def test_verifier_rejects_source_flag_mismatch(tmp_path):
    evidence = make_evidence(tmp_path, replay=True)
    invocation_path = tmp_path / "invocation.json"
    invocation = json.loads(invocation_path.read_text(encoding="utf-8"))
    invocation["replay"] = False
    invocation_path.write_text(json.dumps(invocation), encoding="utf-8")
    with pytest.raises(ValueError, match="Candidate source"):
        verify(evidence)
