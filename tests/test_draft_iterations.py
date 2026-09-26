"""只检查人工构造的逐轮记录，不执行构建。"""
import copy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


class DraftIterationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / 'schemas/draft-iterations.schema.json').read_text())
        cls.validator = Draft202012Validator(cls.schema, format_checker=FormatChecker())
        cls.sample = json.loads((ROOT / 'examples/artifacts/draft-iterations.json').read_text())

    def test_schema_and_example(self):
        Draft202012Validator.check_schema(self.schema)
        self.validator.validate(self.sample)
        self.assertEqual(self.sample['source'], 'MANUAL_EXAMPLE')

    def test_missing_reason_or_changes_rejected(self):
        for key in ('reason', 'changes'):
            sample = copy.deepcopy(self.sample)
            del sample['rounds'][0][key]
            self.assertFalse(self.validator.is_valid(sample))

    def test_pass_requires_zero_exit_code(self):
        sample = copy.deepcopy(self.sample)
        sample['rounds'][0]['build']['exit_code'] = 1
        self.assertFalse(self.validator.is_valid(sample))

    def test_failed_build_can_skip_verification(self):
        sample = copy.deepcopy(self.sample)
        row = sample['rounds'][0]
        row['build'].update(status='FAILED', exit_code=2)
        row['verification'].update(status='NOT_RUN', exit_code=None, log_uri=None)
        self.validator.validate(sample)
        row['verification']['exit_code'] = 0
        self.assertFalse(self.validator.is_valid(sample))

    def test_sample_matches_job_response(self):
        job = json.loads((ROOT / 'examples/draft/succeeded.json').read_text())
        self.assertEqual(self.sample['producer_job_id'], job['job_id'])
        self.assertEqual(self.sample['repository'], job['input']['repository'])
        self.assertEqual(len(self.sample['rounds']), job['output']['iterations'])
        self.assertEqual(self.sample['rounds'][-1]['build']['exit_code'], job['output']['build_result']['exit_code'])
        self.assertEqual(self.sample['rounds'][-1]['verification']['exit_code'], job['output']['verification_result']['exit_code'])
        records = [a for a in job['output']['artifacts'] if a['uri'] == job['output']['iteration_record_uri']]
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['media_type'], 'application/json')


if __name__ == '__main__':
    unittest.main()
