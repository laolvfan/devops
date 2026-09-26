"""MD 报告结构校验；不运行检测器或修复器。"""
import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


class MdReportSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / 'schemas/md-report.schema.json').read_text())
        cls.validator = Draft202012Validator(cls.schema, format_checker=FormatChecker())
        cls.report = json.loads((ROOT / 'examples/artifacts/md-report.json').read_text())

    def test_schema_and_md_example(self):
        Draft202012Validator.check_schema(self.schema)
        self.validator.validate(self.report)

    def test_mixed_report_is_valid(self):
        mixed = json.loads((ROOT / 'examples/artifacts/mixed-report.json').read_text())
        self.validator.validate(mixed)
        self.assertEqual([f['type'] for f in mixed['findings']], ['MISSING', 'REDUNDANT'])

    def test_missing_location_or_evidence_is_rejected(self):
        for key in ('target', 'dependency', 'commit', 'location', 'evidence'):
            report = copy.deepcopy(self.report)
            del report['findings'][0][key]
            with self.subTest(key=key):
                self.assertFalse(self.validator.is_valid(report))
        report = copy.deepcopy(self.report)
        report['findings'][0]['evidence'] = []
        self.assertFalse(self.validator.is_valid(report))

    def test_invalid_type_location_and_commit_are_rejected(self):
        for key, value in [('type', 'MD'), ('commit', 'abc123'),
                           ('location', {'path': 'Makefile', 'line': 0}),
                           ('location', {'path': '../Makefile', 'line': 1})]:
            report = copy.deepcopy(self.report)
            report['findings'][0][key] = value
            with self.subTest(key=key):
                self.assertFalse(self.validator.is_valid(report))

    def test_empty_report_is_valid_analysis_output(self):
        report = copy.deepcopy(self.report)
        report['findings'] = []
        del report['delta']
        self.validator.validate(report)

    def test_incremental_delta_requires_base_commit(self):
        report = copy.deepcopy(self.report)
        del report['delta']['base_commit']
        self.assertFalse(self.validator.is_valid(report))

    def test_manual_evidence_is_labelled(self):
        self.assertEqual(self.report['detector'], 'MANUAL_EXAMPLE')
        kinds = {item['kind'] for item in self.report['findings'][0]['evidence']}
        self.assertIn('FILE_READ', kinds)
        self.assertIn('DECLARATION', kinds)


if __name__ == '__main__':
    unittest.main()
