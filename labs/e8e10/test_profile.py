import json, tempfile, unittest
from pathlib import Path
from lab import fixture,scan,patch,commit

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'sample';fixture(self.p)

    def test_independent_known_edges(self):
        r=scan(self.p)
        self.assertEqual(r['actual']['main.o'],['config.h','main.c'])
        self.assertEqual({(f['type'],f['dependency']) for f in r['findings']},{('MISSING','config.h'),('REDUNDANT','unused.h')})

    def test_unchanged_reuses_both_targets(self):
        r=scan(self.p,scan(self.p));self.assertEqual(r['reused'],['main.o','helper.o']);self.assertEqual(r['refreshed'],[])

    def test_include_added_invalidates_cache(self):
        old=scan(self.p)
        (self.p/'main.c').write_text('#include "extra.h"\n'+(self.p/'main.c').read_text());commit(self.p,'new include')
        r=scan(self.p,old)
        self.assertIn(['MISSING','main.o','extra.h'],r['added']);self.assertEqual(len(r['refreshed']),2)

    def test_patch_preserves_redundant_dependency(self):
        r=scan(self.p);diff,plan=patch(self.p,r)
        self.assertIn('+main.o: main.c unused.h config.h',diff)
        self.assertNotIn('-\tgcc',diff)
        self.assertNotIn('config.h',(self.p/'Makefile').read_text())

    def test_old_report_rejected(self):
        r=scan(self.p);r['commit']='0'*40
        with self.assertRaisesRegex(ValueError,'STALE_REPORT'):patch(self.p,r)

    def test_unsafe_dependency_rejected(self):
        r=scan(self.p);r['findings']=[{'type':'MISSING','target':'main.o','dependency':'../outside.h'}]
        with self.assertRaisesRegex(ValueError,'UNSAFE_PATH'):patch(self.p,r)

    def test_unsupported_configuration_rejected(self):
        (self.p/'Makefile').write_text((self.p/'Makefile').read_text().replace('-O0','-include unknown.h'))
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_FLAGS'):scan(self.p)

class Student241880100B(unittest.TestCase):
    """Independent expected outcomes for report, style and acceptance boundaries."""

    def test_e8_unknown_target_rejected_without_writing_source(self):
        from lab import patch, scan
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'sample'
            fixture(project)
            before = (project / 'Makefile').read_bytes()
            report = scan(project)
            report['findings'] = [{'type': 'MISSING', 'target': 'ghost.o', 'dependency': 'config.h'}]
            with self.assertRaisesRegex(ValueError, '^UNSUPPORTED_TARGET$'):
                patch(project, report)
            self.assertEqual((project / 'Makefile').read_bytes(), before)

    def test_e9_renamed_macro_updates_definition_and_preserves_reference(self):
        from lab import commit, patch, run, scan
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'sample'
            fixture(project, 'macro')
            makefile = project / 'Makefile'
            makefile.write_text(makefile.read_text().replace('DEPS', 'SOURCES'))
            commit(project, 'rename dependency variable')
            before = makefile.read_bytes()
            diff, plan = patch(project, scan(project))
            self.assertIn('+SOURCES = main.c unused.h config.h', diff)
            self.assertEqual(plan, [{'target': 'main.o', 'dependency': 'config.h', 'style': 'macro'}])
            self.assertEqual(makefile.read_bytes(), before)
            candidate = Path(directory) / 'candidate.patch'
            candidate.write_text(diff)
            run(['git', 'apply', '--check', str(candidate)], project)
            run(['git', 'apply', str(candidate)], project)
            self.assertIn('main.o: $(SOURCES)', makefile.read_text())
            self.assertIn('unused.h', makefile.read_text())
            self.assertFalse(any(f['type'] == 'MISSING' for f in scan(project)['findings']))

    def test_e10_build_success_cannot_hide_remaining_missing_dependency(self):
        import difflib
        from lab import validate
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / 'sample'
            fixture(project)
            before = (project / 'Makefile').read_bytes()
            original = before.decode()
            changed = original.replace('CFLAGS = -O0', 'CFLAGS = -O1')
            candidate = root / 'candidate.patch'
            candidate.write_text(''.join(difflib.unified_diff(
                original.splitlines(True), changed.splitlines(True),
                fromfile='a/Makefile', tofile='b/Makefile')))
            result = validate(project, candidate, root / 'validation')
            self.assertTrue(result['checks']['patch_applies'])
            self.assertTrue(result['checks']['build'])
            self.assertTrue(result['checks']['test'])
            self.assertFalse(result['checks']['header_change'])
            self.assertFalse(result['checks']['no_missing'])
            self.assertFalse(result['accepted'])
            self.assertTrue(result['rollback'])
            self.assertTrue(result['source_unchanged'])
            self.assertEqual((project / 'Makefile').read_bytes(), before)

class Student241880326E8(unittest.TestCase):
    def test_redundant_only_does_not_remove_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'sample'
            fixture(project)

            before = (project / 'Makefile').read_bytes()
            report = scan(project)

            # 构造只包含冗余依赖的报告，作为本测试的输入。
            report['findings'] = [
                finding for finding in report['findings']
                if finding['type'] == 'REDUNDANT'
            ]

            self.assertEqual(
                [(f['target'], f['dependency']) for f in report['findings']],
                [('main.o', 'unused.h')]
            )

            diff, plan = patch(project, report)

            self.assertEqual(diff, '')
            self.assertEqual(plan, [])
            self.assertEqual((project / 'Makefile').read_bytes(), before)

class StudentE9B(unittest.TestCase):
    def test_macro_style_patch_updates_definition(self):
        import tempfile
        from pathlib import Path
        from lab import fixture, patch, scan, run

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "sample"
            fixture(project, "macro")
            diff, plan = patch(project, scan(project))
            candidate = Path(directory) / "candidate.patch"
            candidate.write_text(diff)
            run(["git", "apply", str(candidate.resolve())], project)

            makefile = (project / "Makefile").read_text()
            self.assertIn("DEPS = main.c unused.h config.h", makefile)
            self.assertIn("main.o: $(DEPS)", makefile)
            self.assertEqual(plan[0]["style"], "macro")
            self.assertFalse(any(item["type"] == "MISSING"
                                 for item in scan(project)["findings"]))

if __name__=='__main__':unittest.main()
