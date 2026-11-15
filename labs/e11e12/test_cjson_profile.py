import subprocess
import tempfile
import unittest
from pathlib import Path

try:
    import cjson_profile
except ModuleNotFoundError:
    cjson_profile = None

class CjsonProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "cJSON.h").write_text("#define VALUE 1\n")
        (self.root / "cJSON_Utils.h").write_text('#include "cJSON.h"\n')
        (self.root / "cJSON_Utils.c").write_text('#include "cJSON_Utils.h"\nint value(void) { return VALUE; }\n')
        (self.root / "Makefile").write_text("UTILS_OBJ = cJSON_Utils.o\n$(UTILS_OBJ): cJSON_Utils.c cJSON_Utils.h\n\t$(CC) -c cJSON_Utils.c -o $@\n")
        with (self.root / "Makefile").open("a") as makefile:
            makefile.write(".PHONY: clean test\nclean:\n\trm -f cJSON_Utils.o\ntest:\n\t@true\n")
        for args in (["init", "-q", "-b", "main"], ["config", "user.name", "Test"], ["config", "user.email", "test@example.invalid"], ["add", "."], ["commit", "-qm", "fixture"]):
            subprocess.run(["git", "-C", str(self.root), *args], check=True)
        self.addCleanup(self.tmp.cleanup)

    def test_detects_and_repairs_transitive_header_dependency(self):
        self.assertIsNotNone(cjson_profile, "cJSON profile must be available")
        report = cjson_profile.scan(self.root)
        self.assertIn({"type": "MISSING", "target": "cJSON_Utils.o", "dependency": "cJSON.h"}, report["findings"])
        diff, edits = cjson_profile.patch(self.root, report)
        self.assertIn("+$(UTILS_OBJ): cJSON_Utils.c cJSON_Utils.h cJSON.h", diff)
        self.assertEqual(edits[0]["dependency"], "cJSON.h")
        self.assertNotIn("cJSON.h\n", (self.root / "Makefile").read_text())

    def test_stale_report_is_rejected(self):
        self.assertIsNotNone(cjson_profile)
        report = cjson_profile.scan(self.root)
        report["commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "STALE_REPORT"):
            cjson_profile.patch(self.root, report)

    def test_validation_runs_real_rebuild_after_header_change(self):
        self.assertIsNotNone(cjson_profile)
        report = cjson_profile.scan(self.root)
        diff, _ = cjson_profile.patch(self.root, report)
        patch_path = self.root.parent / (self.root.name + ".patch")
        patch_path.write_text(diff)
        self.addCleanup(patch_path.unlink, missing_ok=True)
        evidence = self.root.parent / (self.root.name + "-evidence")
        self.addCleanup(__import__("shutil").rmtree, evidence, ignore_errors=True)
        result = cjson_profile.validate(self.root, patch_path, evidence)
        self.assertTrue(result["accepted"], result)
        self.assertTrue(result["checks"]["header_change"])
        self.assertTrue(result["checks"]["no_missing"])
        self.assertIn("cJSON_Utils.h cJSON.h", (self.root / "Makefile").read_text())

    def test_pipeline_accepts_cjson_snapshot(self):
        import pipeline
        (self.root / "cJSON.c").write_text("int placeholder(void) {return 0;}\n")
        subprocess.run(["git", "-C", str(self.root), "add", "cJSON.c"], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "add source"], check=True)
        destination = self.root.parent / (self.root.name + "-snapshot")
        logs = self.root.parent / (self.root.name + "-logs")
        self.addCleanup(__import__("shutil").rmtree, destination, ignore_errors=True)
        self.addCleanup(__import__("shutil").rmtree, logs, ignore_errors=True)
        sha = pipeline.snapshot(self.root, "HEAD", destination, logs, profile="cjson")
        self.assertEqual(sha, subprocess.check_output(["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True).strip())

    def test_api_rejects_broken_dockerfile_outside_data(self):
        import pipeline
        import server
        with tempfile.TemporaryDirectory() as d:
            store = server.Store(Path(d) / "jobs")
            request = {"mode": "e12", "repo": str(pipeline.ROOT / "data/p"),
                       "base": "a", "target": "b", "broken_dockerfile": str(Path(d) / "outside")}
            try:
                with self.assertRaisesRegex(ValueError, "broken_dockerfile"):
                    store.submit(request, "k")
            finally:
                store.pool.shutdown()

    def test_candidate_preserves_original_commands(self):
        import pipeline
        from draft.autobuild import prepare_candidate
        folder = pipeline.ROOT / "labs/e11e12/examples"
        broken = (folder / "cjson.Dockerfile.broken").read_text()
        candidate = (folder / "cjson.Dockerfile.candidate").read_text()
        baseline = prepare_candidate(broken, candidate)
        self.assertIn("RUN make cJSON_Utils.o", baseline)
        self.assertIn("RUN make test", baseline)
        self.assertIn("build-essential", candidate)

if __name__ == "__main__":
    unittest.main()
