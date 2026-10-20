"""Independent, hand-authored reports exercise the real E7 oracle.

These are synthetic unit-test inputs; no report here proves a Docker run.
"""
import copy
import importlib.util
from pathlib import Path
import unittest


RUNNER = Path(__file__).resolve().parents[2] / "scripts/run_e7_b_gate.py"
SPEC = importlib.util.spec_from_file_location("e7_gate", RUNNER)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)
IMAGE = "sha256:" + "b" * 64


def successful_report():
    return {
        "trace_id": "e7-unit-synthetic",
        "status": "SUCCEEDED",
        "attempts": [
            {"iteration": 1, "build_exit_code": 1, "failure_class": "MISSING_MAKE"},
            {"iteration": 2, "build_exit_code": 0, "image_id": IMAGE},
        ],
        "verification": {
            "command": ["docker", "run", "--rm", "--network", "none", IMAGE],
            "exit_code": 0,
            "expected_output": "hello E3",
            "actual_output": "hello E3\n",
            "output_matches": True,
        },
    }


class GateExpectationTests(unittest.TestCase):
    def test_accepts_complete_success(self):
        GATE.evaluate("success", 0, successful_report())

    def test_rejects_running_a_different_image(self):
        report = successful_report()
        report["verification"]["command"][-1] = "sha256:" + "c" * 64
        with self.assertRaises(ValueError):
            GATE.evaluate("success", 0, report)

    def test_rejects_infrastructure_failure_as_reproduction(self):
        report = successful_report()
        report["attempts"][0]["failure_class"] = "INFRASTRUCTURE"
        with self.assertRaises(ValueError):
            GATE.evaluate("success", 0, report)

    def test_rejects_build_timeout_as_runtime_timeout(self):
        report = successful_report()
        report.pop("verification")
        report.update(status="TIMED_OUT", error="Docker client command exceeded 600s")
        report["attempts"][1]["build_exit_code"] = 124
        with self.assertRaises(ValueError):
            GATE.evaluate("runtime-timeout", 1, report)

    def test_expected_faults_are_accepted(self):
        mismatch = successful_report()
        mismatch["status"] = "FAILED"
        mismatch["verification"].update(
            expected_output="intentionally wrong output", output_matches=False
        )
        invalid = {
            "status": "FAILED",
            "error": "Candidate changed required project/build/runtime instructions",
            "attempts": [],
        }
        failed = successful_report()
        failed.pop("verification")
        failed.update(status="FAILED", error="Repair candidate build failed; inspect iter-02 logs")
        failed["attempts"][1]["build_exit_code"] = 1
        timeout = successful_report()
        timeout.pop("verification")
        timeout.update(status="TIMED_OUT", error="Docker client command exceeded 1s")
        for name, report in (
            ("wrong-output", mismatch), ("invalid-candidate", invalid),
            ("build-failed", failed), ("runtime-timeout", timeout),
        ):
            with self.subTest(case=name):
                GATE.evaluate(name, 1, report)

    def test_failed_build_must_not_verify_a_program(self):
        report = copy.deepcopy(successful_report())
        report.update(status="FAILED", error="Repair candidate build failed; inspect iter-02 logs")
        report["attempts"][1]["build_exit_code"] = 1
        with self.assertRaises(ValueError):
            GATE.evaluate("build-failed", 1, report)


if __name__ == "__main__":
    unittest.main()
