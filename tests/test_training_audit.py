import copy
import unittest

from scripts.audit_training_data import leaves, prepare, validate, resolve_source_quotes


class TrainingAuditTests(unittest.TestCase):
    def test_frozen_sample_is_training_only_and_reproducible(self):
        manifest,samples=prepare()
        self.assertEqual(prepare(),(manifest,samples))
        self.assertEqual(len({r['case_id'] for r in samples}),100)
        self.assertTrue(all(r['case_id'].startswith('train:') for r in samples))
        self.assertEqual(sum(r['group']=='random' for r in samples),50)
        self.assertEqual(sum(r['group']=='targeted' for r in samples),50)

    def test_evidence_checks_reject_fabricated_quotes_and_wrong_leaf(self):
        sample=dict(note='A woman received drug A 5 mg. No fever.',reference='{"treatments":[{"name":"drug A","dosage":"5 mg"}]}',
                    leaves=leaves({'treatments':[{'name':'drug A','dosage':'5 mg'}]}))
        check=dict(field_path='/treatments/0/dosage',label_excerpt='5 mg',source_quote='drug A 5 mg',explanation='Dose paired.')
        review=dict(supported_checks=[copy.deepcopy(check) for _ in range(3)],findings=[])
        validate(review,sample)
        for key,value in [('source_quote','drug B 5 mg'),('label_excerpt','50 mg'),('field_path','/treatments/0/name')]:
            broken=copy.deepcopy(review); broken['supported_checks'][0][key]=value
            with self.assertRaises(AssertionError): validate(broken,sample)

    def test_quote_recovery_keeps_signs_and_words_exact(self):
        sample={'note':'Started intravenous (IV) drug A (5 mg every 12 hours); CK20 (+).'}
        row={'source_quote':'IV drug A (5 mg every 12 hours)'}
        review={'supported_checks':[row], 'findings':[]}
        self.assertEqual(len(resolve_source_quotes(review,sample)),1)
        self.assertIn(row['source_quote'],sample['note'])
        bad={'supported_checks':[{'source_quote':'CK20 (-)'}], 'findings':[]}
        self.assertEqual(resolve_source_quotes(bad,sample),[])


if __name__=='__main__': unittest.main()
