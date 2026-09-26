"""运行：python -m unittest discover -s tests -v（需 jsonschema[format]）。"""
import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA = json.loads((Path(__file__).resolve().parents[1] / 'schemas/task.schema.json').read_text())
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
REPO = {'url': 'https://example.com/project.git', 'commit': 'a' * 40}
ENV = {'image_uri': 'artifact://job-DRAFT-001/image-001/image',
       'configuration_id': 'cfg-ubuntu22-gcc12-release-v1'}
INPUTS = {
    'DRAFT': {'build_command': 'make', 'verify_command': 'make test'},
    'FULL_CHECK': {'environment': ENV, 'clean_build_command': 'make clean && make', 'project_root': '/project'},
    'INCREMENTAL_CHECK': {'environment': ENV, 'build_command': 'make', 'base_commit': 'b' * 40,
                          'baseline': {'actual_graph_uri': 'artifact://job-FULL_CHECK-001/graph-001/actual.json',
                                       'commit': 'b' * 40, 'configuration_id': ENV['configuration_id']}},
    'REPAIR': {'environment': ENV, 'build_command': 'make', 'verify_command': 'make test',
               'makefile_path': 'Makefile', 'md_report_uri': 'artifact://job-FULL_CHECK-001/report-001/md.json'},
}
OUTPUTS = {
    'DRAFT': ['DOCKERFILE', 'DOCKER_IMAGE', 'BUILD_LOG'],
    'FULL_CHECK': ['ACTUAL_GRAPH', 'DECLARED_GRAPH', 'ERROR_REPORT', 'BUILD_LOG'],
    'INCREMENTAL_CHECK': ['ACTUAL_GRAPH', 'ERROR_REPORT'],
    'REPAIR': ['PATCH', 'BUILD_LOG', 'TEST_RESULT', 'ERROR_REPORT'],
}


def request(kind):
    return {'schema_version': '1.0.0', 'trace_id': 'trace-001', 'job_type': kind,
            'idempotency_key': 'key-001',
            'input': copy.deepcopy({'repository': REPO, 'timeout_seconds': 1800, **INPUTS[kind]})}


def response(kind, status='SUCCEEDED'):
    value = request(kind)
    del value['idempotency_key']
    if kind == 'DRAFT':
        value['input']['max_iterations'] = 20
    job_id = f'job-{kind}-001'
    value.update(job_id=job_id, status=status, output=None, error=None,
                 execution={'attempt': 1, 'queued_at': '2026-09-26T10:00:00+08:00', 'timeout_seconds': 1800})
    if status != 'QUEUED':
        value['execution']['started_at'] = '2026-09-26T10:00:01+08:00'
    if status not in ('QUEUED', 'RUNNING'):
        value['execution'].update(finished_at='2026-09-26T10:00:02+08:00', duration_ms=1000)
    if status == 'SUCCEEDED':
        value['output'] = {'artifacts': [
            {'artifact_id': f'art-{i}', 'type': kind_, 'uri': f'artifact://{job_id}/art-{i}/result',
             'media_type': 'application/octet-stream', 'producer_job_id': job_id,
             'commit': REPO['commit'], 'configuration_id': ENV['configuration_id']}
            for i, kind_ in enumerate(OUTPUTS[kind])]}
        if kind == 'DRAFT':
            value['output'].update(
                build_result={'command': 'make', 'exit_code': 0},
                verification_result={'command': 'make test', 'exit_code': 0},
                iterations=1,
                iteration_record_uri=f'artifact://{job_id}/iterations-001/iterations.json')
        elif kind == 'REPAIR':
            value['output'].update(
                patch_accepted=True, declaration_style='Add prerequisite to the existing rule',
                validation={'build_exit_code': 0, 'test_exit_code': 0,
                            'remaining_missing': 0, 'workspace': 'Source plus candidate patch'})
    elif status in ('FAILED', 'TIMED_OUT', 'CANCELLED'):
        value['error'] = {'code': {'FAILED': 'ENV_3002', 'TIMED_OUT': 'EXEC_4002', 'CANCELLED': 'EXEC_4003'}[status],
                          'message': 'Execution stopped', 'retryable': False, 'details': {}, 'log_uri': None}
    return value


class TaskSchemaTests(unittest.TestCase):
    def test_schema_is_valid(self):
        Draft202012Validator.check_schema(SCHEMA)

    def test_all_task_requests_and_states(self):
        for kind in INPUTS:
            with self.subTest(kind=kind, shape='request'):
                VALIDATOR.validate(request(kind))
            for status in ('QUEUED', 'RUNNING', 'SUCCEEDED', 'FAILED', 'TIMED_OUT', 'CANCELLED'):
                with self.subTest(kind=kind, status=status):
                    VALIDATOR.validate(response(kind, status))

    def test_invalid_inputs_are_rejected(self):
        cases = []
        value = request('DRAFT'); value['job_type'] = 'ABC'; cases.append(value)
        value = request('INCREMENTAL_CHECK'); del value['input']['baseline']; cases.append(value)
        value = request('REPAIR'); del value['input']['md_report_uri']; cases.append(value)
        value = request('DRAFT'); value['job_id'] = 'job-DRAFT-001'; cases.append(value)
        for field, bad in [('timeout_seconds', 0), ('timeout_seconds', '1800'), ('max_iterations', 51)]:
            value = request('DRAFT'); value['input'][field] = bad; cases.append(value)
        value = request('FULL_CHECK'); value['input']['repository']['commit'] = 'abc123'; cases.append(value)
        for i, value in enumerate(cases):
            with self.subTest(case=i):
                self.assertFalse(VALIDATOR.is_valid(value))

    def test_invalid_results_are_rejected(self):
        for kind in INPUTS:
            value = response(kind); value['output']['artifacts'].pop()
            with self.subTest(kind=kind):
                self.assertFalse(VALIDATOR.is_valid(value))
        cases = []
        value = response('DRAFT'); value['output'] = None; cases.append(value)
        value = response('DRAFT', 'FAILED'); value['error'] = None; cases.append(value)
        value = response('DRAFT', 'FAILED'); value['output'] = response('DRAFT')['output']; cases.append(value)
        value = response('DRAFT'); value['execution']['started_at'] = 'yesterday'; cases.append(value)
        value = response('DRAFT'); del value['execution']['finished_at']; cases.append(value)
        value = response('DRAFT', 'TIMED_OUT'); value['error']['code'] = 'ENV_3002'; cases.append(value)
        for i, value in enumerate(cases):
            with self.subTest(case=i):
                self.assertFalse(VALIDATOR.is_valid(value))

    def test_optional_extensions_and_defaults(self):
        value = request('DRAFT')
        value['optional_note'] = 'compatible extension'
        VALIDATOR.validate(value)
        self.assertNotIn('max_iterations', value['input'])

    def test_cancellation_before_start(self):
        value = response('DRAFT', 'CANCELLED')
        value['execution']['started_at'] = None
        value['execution']['duration_ms'] = None
        VALIDATOR.validate(value)


if __name__ == '__main__':
    unittest.main()
