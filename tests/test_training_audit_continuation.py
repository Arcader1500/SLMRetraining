import unittest

from scripts.continue_training_audit import (
    CALIBRATION_IDS,
    append_calibration_policy,
    next_cases,
    validate_source_review,
)
from scripts.audit_training_data import prepare


class TrainingAuditContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.samples = {row['case_id']: row for row in prepare()[1]}

    def test_calibration_is_four_existing_pilot_cases(self):
        self.assertEqual(CALIBRATION_IDS, ('train:119', 'train:1052', 'train:24', 'train:1453'))
        self.assertTrue(set(CALIBRATION_IDS) <= self.samples.keys())

    def test_appendix_preserves_base_rubric(self):
        base = 'unchanged rubric'
        result = append_calibration_policy(base)
        self.assertTrue(result.startswith(base + '\n\nCALIBRATION APPENDIX:'))
        self.assertIn('ordinary history', result.casefold())
        self.assertIn('emergency-department presentation', result)

    def test_resume_skips_checkpointed_cases_in_interleaved_order(self):
        samples = [dict(case_id=f'r{i}', group='random') for i in range(3)]
        samples += [dict(case_id=f't{i}', group='targeted') for i in range(3)]
        self.assertEqual([s['case_id'] for s in next_cases(samples, {'r0','t0'})], ['r1','t1','r2','t2'])

    def test_source_review_requires_verbatim_quote_and_valid_disposition(self):
        sample = self.samples['train:119']
        result = {'candidate_dispositions': [], 'added_findings': []}
        validate_source_review(result, sample)
        result['added_findings'] = [dict(field_path='/treatments', label_excerpt='',
            source_quote='not in source', category='omission', classification='material_omission',
            disposition='confirmed', attribution='projection_loss', explanation='test')]
        with self.assertRaises(AssertionError):
            validate_source_review(result, sample)

    def test_source_review_must_account_for_every_candidate_once(self):
        sample = self.samples['train:119']
        candidate = {'findings': [dict(field_path='/treatments/0/name')]}
        review = {'candidate_dispositions': [], 'added_findings': []}
        with self.assertRaises(AssertionError):
            validate_source_review(review, sample, candidate)


if __name__ == '__main__':
    unittest.main()
