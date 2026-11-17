"""E13 fixed-report transfer integrity at the B pipeline entry."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import lab
import pipeline


class FixedReportTransferTests(unittest.TestCase):
    def check_transfer(self, tamper):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project = root / "repo"
            lab.fixture(project)
            report = lab.scan(project)
            sha = report["commit"]
            envelope = dict(schema_version="e11e12-1", kind="fixed-md",
                            status="SUCCEEDED", commit=sha, data=report)
            fixed = root / "fixed.json"
            fixed.write_text(json.dumps(envelope))
            expected = hashlib.sha256(fixed.read_bytes()).hexdigest()
            if tamper:
                fixed.write_bytes(fixed.read_bytes() + b"\n")
            before = (project / "Makefile").read_bytes()
            request = dict(mode="e11-b", repo=str(project), base=sha, target=sha,
                           candidate=str(root / "unused.Dockerfile"),
                           fixed_report=str(fixed), fixed_report_sha256=expected)

            def draft(_project, _candidate, output, *_args, **_kwargs):
                result = {"status": "SUCCEEDED"}
                lab.save(output / "result.json", result)
                return result

            # Real snapshot and report checks; isolate the preceding Docker build
            # and stop at repair so this contract test needs no Docker daemon.
            with patch("draft.autobuild.auto_build", side_effect=draft), patch(
                "pipeline.patch", side_effect=pipeline.Failure("TEST_STOP", "repair reached")
            ) as repair:
                result = pipeline.execute(request, root / "output")
            self.assertEqual(result["status"], "FAILED")
            self.assertEqual((project / "Makefile").read_bytes(), before)
            if tamper:
                self.assertEqual(result["error"]["code"], "ARTIFACT_HASH_MISMATCH")
                repair.assert_not_called()
                self.assertFalse((root / "output" / "fixed-md-input.json").exists())
            else:
                self.assertEqual(result["error"]["code"], "TEST_STOP")
                repair.assert_called_once()
                self.assertEqual(
                    json.loads((root / "output" / "fixed-md-input.json").read_text()), envelope
                )

    def test_changed_report_with_old_hash_is_rejected_before_repair(self):
        self.check_transfer(True)

    def test_matching_report_hash_reaches_repair(self):
        self.check_transfer(False)
