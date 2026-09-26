"""HTTP 回执和成功结果的文件校验，不调用真实 API。"""
import copy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'schemas/task.schema.json').read_text())


def validator(entry):
    return Draft202012Validator({'$ref': f'#/$defs/{entry}', '$defs': SCHEMA['$defs']}, format_checker=FormatChecker())


def example(path):
    return json.loads((ROOT / 'examples' / path).read_text())


class ResponseFormatTests(unittest.TestCase):
    def test_all_accepted_receipts(self):
        for folder in ('draft', 'repair', 'full_check', 'incremental_check'):
            validator('acceptedResponse').validate(example(f'{folder}/accepted.json'))

    def test_accepted_requires_job_id_and_queued(self):
        value = example('draft/accepted.json')
        value['status'] = 'SUCCEEDED'
        self.assertFalse(validator('acceptedResponse').is_valid(value))
        del value['job_id']
        value['status'] = 'QUEUED'
        self.assertFalse(validator('acceptedResponse').is_valid(value))

    def test_bad_requests_and_missing_trace(self):
        for path in ('unknown-job-type', 'missing-baseline'):
            validator('badRequestResponse').validate(example(f'http-errors/{path}.json'))
        value = example('http-errors/unknown-job-type.json')
        value['trace_id'] = None
        validator('badRequestResponse').validate(value)
        value['job_id'] = 'job-DRAFT-001'
        self.assertFalse(validator('badRequestResponse').is_valid(value))
        del value['job_id']
        value['error']['code'] = 'ENV_3002'
        self.assertFalse(validator('badRequestResponse').is_valid(value))

    def test_draft_requires_successful_results_and_record(self):
        valid = example('draft/succeeded.json')
        validator('jobResponse').validate(valid)
        for field in ('build_result', 'verification_result', 'iterations', 'iteration_record_uri'):
            value = copy.deepcopy(valid)
            del value['output'][field]
            self.assertFalse(validator('jobResponse').is_valid(value))
        value = copy.deepcopy(valid)
        value['output']['verification_result']['exit_code'] = 1
        self.assertFalse(validator('jobResponse').is_valid(value))

    def test_repair_requires_accepted_patch_and_zero_missing(self):
        valid = example('repair/succeeded.json')
        validator('jobResponse').validate(valid)
        for field in ('patch_accepted', 'declaration_style', 'validation'):
            value = copy.deepcopy(valid)
            del value['output'][field]
            self.assertFalse(validator('jobResponse').is_valid(value))
        for field in ('build_exit_code', 'test_exit_code', 'remaining_missing'):
            value = copy.deepcopy(valid)
            value['output']['validation'][field] = 1
            self.assertFalse(validator('jobResponse').is_valid(value))
        value = copy.deepcopy(valid)
        value['output']['patch_accepted'] = False
        self.assertFalse(validator('jobResponse').is_valid(value))

    def test_image_ref_cannot_be_empty(self):
        value = example('draft/succeeded.json')
        for item in value['output']['artifacts']:
            if item['type'] == 'DOCKER_IMAGE':
                item['image_ref'] = ''
        self.assertFalse(validator('jobResponse').is_valid(value))


if __name__ == '__main__':
    unittest.main()
