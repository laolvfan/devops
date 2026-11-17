import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pipeline
import server

class Contracts(unittest.TestCase):
    def report(self):return {'schema_version':'e11e12-1','kind':'incremental-check','commit':'a'*40,'status':'SUCCEEDED'}
    def test_accept_current_report(self):pipeline.check_envelope(self.report(),'a'*40,'incremental-check')
    def test_reject_old_commit(self):
        with self.assertRaisesRegex(pipeline.Failure,'another commit'):pipeline.check_envelope(self.report(),'b'*40)
    def test_reject_schema(self):
        r=self.report();r['schema_version']='old'
        with self.assertRaises(pipeline.Failure):pipeline.check_envelope(r,'a'*40)
    def test_reject_failed_upstream(self):
        r=self.report();r['status']='FAILED'
        with self.assertRaises(pipeline.Failure):pipeline.check_envelope(r,'a'*40)
    def test_reject_wrong_artifact_kind(self):
        with self.assertRaises(pipeline.Failure):pipeline.check_envelope(self.report(),'a'*40,'fixed-md')
    def test_artifact_uses_relative_uri_and_content_hash(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'x.json';p.write_text('{}')
            a=pipeline.artifact(p,root,'job-1');self.assertEqual(a['uri'],'artifact://job-1/x.json');self.assertEqual(len(a['sha256']),64)
    def test_existing_evidence_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'keep').write_text('keep')
            with self.assertRaises(pipeline.Failure):pipeline.execute({},root)
            self.assertEqual((root/'keep').read_text(),'keep')
    def test_changed_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'r.json';p.write_text('{}')
            with self.assertRaises(pipeline.Failure):pipeline.load_artifact(p,'0'*64)
    def test_b_pipeline_checks_fixed_report_hash(self):
        import hashlib
        import json
        import draft.autobuild

        sha = 'a' * 40
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            repo = root / 'repo'
            repo.mkdir()
            report = root / 'fixed.json'
            report.write_text(json.dumps({
                'schema_version': 'e11e12-1',
                'kind': 'fixed-md',
                'commit': sha,
                'status': 'SUCCEEDED',
                'data': {'commit': sha}
            }))
            digest = hashlib.sha256(report.read_bytes()).hexdigest()

            def fake_snapshot(repo, commit, dest, logs, profile):
                dest.mkdir(parents=True)
                (dest / 'Makefile').write_text('all:\\n')
                return sha

            def fake_build(target, candidate, out, expected, timeout):
                out.mkdir(parents=True)
                (out / 'result.json').write_text('{}')
                return {'status': 'SUCCEEDED'}

            request = {
                'mode': 'e11-b',
                'repo': str(repo),
                'base': sha,
                'target': sha,
                'candidate': str(root / 'Dockerfile'),
                'fixed_report': str(report),
                'fixed_report_sha256': digest
            }
            with patch.object(pipeline, 'snapshot', side_effect=fake_snapshot), \
                 patch.object(draft.autobuild, 'auto_build', side_effect=fake_build), \
                 patch.object(pipeline, 'patch', return_value=('', [])):
                good = pipeline.execute(request, root / 'good')
                self.assertIn('fixed-md', [s['name'] for s in good['stages']])

                report.write_text(report.read_text() + ' ')
                bad = pipeline.execute(request, root / 'bad')
                self.assertEqual(bad['error']['code'], 'ARTIFACT_HASH_MISMATCH')

    def test_same_key_same_request_same_job(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);store=server.Store(root/'jobs')
            request={'mode':'e11-a','repo':str(pipeline.ROOT/'data/p'),'base':'a','target':'b'}
            with patch.object(store.pool,'submit'):
                one=store.submit(request,'same');two=store.submit(request,'same')
                self.assertEqual(one['job_id'],two['job_id'])
                changed=dict(request,target='c')
                with self.assertRaisesRegex(ValueError,'IDEMPOTENCY_CONFLICT'):store.submit(changed,'same')
            store.pool.shutdown()
    def test_api_rejects_repo_outside_data(self):
        with tempfile.TemporaryDirectory() as d:
            store=server.Store(Path(d)/'jobs')
            with self.assertRaises(ValueError):store.submit({'mode':'e11-a','repo':str(Path(d)),'base':'a','target':'b'},'k')
            store.pool.shutdown()

if __name__=='__main__':unittest.main()
