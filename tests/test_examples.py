"""校验磁盘上的演示数据，不执行真实构建或检测。"""
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'examples'
SCHEMA = json.loads((ROOT / 'schemas/task.schema.json').read_text())
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
FOLDERS = ('draft', 'full_check', 'incremental_check', 'repair')


def read(path):
    return json.loads((EXAMPLES / path).read_text())


def artifact(response, kind):
    return next(a for a in response['output']['artifacts'] if a['type'] == kind)


class ExampleTests(unittest.TestCase):
    def test_requests_and_query_responses(self):
        for folder in FOLDERS:
            for name in ('request', 'succeeded', 'failed'):
                with self.subTest(folder=folder, name=name):
                    VALIDATOR.validate(read(f'{folder}/{name}.json'))
        for state in ('queued', 'running'):
            VALIDATOR.validate(read(f'draft/{state}.json'))

    def test_negative_examples_and_http_error_proposals(self):
        for name in ('unknown-job-type', 'missing-baseline'):
            self.assertFalse(VALIDATOR.is_valid(read(f'invalid/{name}.json')))
            error = read(f'http-errors/{name}.json')
            self.assertNotIn('job_id', error)
            self.assertEqual(error['error']['code'], 'REQUEST_1001')
            VALIDATOR.evolve(schema={'$ref': '#/$defs/error', '$defs': SCHEMA['$defs']}).validate(error['error'])

    def test_receipts_and_success_results_match_requests(self):
        for folder in FOLDERS:
            with self.subTest(folder=folder):
                request = read(f'{folder}/request.json')
                accepted = read(f'{folder}/accepted.json')
                response = read(f'{folder}/succeeded.json')
                self.assertEqual(accepted['status'], 'QUEUED')
                self.assertEqual(accepted['job_id'], response['job_id'])
                self.assertEqual(accepted['schema_version'], request['schema_version'])
                self.assertEqual(accepted['trace_id'], request['trace_id'])
                self.assertEqual(response['trace_id'], request['trace_id'])
                expected = request['input'].copy()
                if folder == 'draft':
                    expected['max_iterations'] = 20
                self.assertEqual(response['input'], expected)
                for item in response['output']['artifacts']:
                    self.assertEqual(item['producer_job_id'], response['job_id'])
                    self.assertEqual(item['commit'], request['input']['repository']['commit'])
                failed = read(f'{folder}/failed.json')
                self.assertNotEqual(failed['job_id'], response['job_id'])

    def test_cross_service_handoffs(self):
        draft = read('draft/succeeded.json')
        full = read('full_check/succeeded.json')
        incremental = read('incremental_check/succeeded.json')
        repair = read('repair/request.json')
        image = artifact(draft, 'DOCKER_IMAGE')
        graph = artifact(full, 'ACTUAL_GRAPH')
        for task in (full, incremental, repair):
            self.assertEqual(task['input']['environment']['image_uri'], image['uri'])
            self.assertEqual(task['input']['environment']['configuration_id'], image['configuration_id'])
            self.assertEqual(task['trace_id'], draft['trace_id'])
        baseline = incremental['input']['baseline']
        self.assertEqual(baseline['actual_graph_uri'], graph['uri'])
        self.assertEqual(baseline['commit'], graph['commit'])
        self.assertEqual(baseline['commit'], incremental['input']['base_commit'])
        self.assertEqual(baseline['configuration_id'], graph['configuration_id'])
        self.assertEqual(repair['input']['md_report_uri'], artifact(incremental, 'ERROR_REPORT')['uri'])
        self.assertEqual(repair['input']['repository'], incremental['input']['repository'])

    def test_manual_md_report_matches_repair_input(self):
        report = read('artifacts/md-report.json')
        repair = read('repair/request.json')['input']
        incremental = read('incremental_check/succeeded.json')
        self.assertEqual(report['repository'], repair['repository'])
        self.assertEqual(report['configuration_id'], repair['environment']['configuration_id'])
        self.assertEqual(report['producer_job_id'], incremental['job_id'])
        self.assertEqual(report['detector'], 'MANUAL_EXAMPLE')
        self.assertTrue(report['findings'])
        for finding in report['findings']:
            self.assertEqual(finding['type'], 'MISSING')
            self.assertEqual(finding['commit'], repair['repository']['commit'])
            self.assertTrue(finding['evidence'])
        self.assertEqual(report['delta']['added'], [f['finding_id'] for f in report['findings']])
        self.assertEqual(incremental['status'], 'SUCCEEDED')
        self.assertIsNone(incremental['error'])


if __name__ == '__main__':
    unittest.main()
