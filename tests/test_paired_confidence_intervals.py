import unittest

import numpy as np
from scipy.stats import bootstrap

from scripts.calculate_paired_confidence_intervals import mean_difference, paired_statistics


class PairedConfidenceIntervalTests(unittest.TestCase):
    def test_constant_gain_preserves_pairing(self):
        baseline=np.arange(10,dtype=float)/10
        result=paired_statistics(baseline,baseline+.2,resamples=2000)
        np.testing.assert_allclose(result['ci95_bca'],[.2,.2],atol=1e-12)
        self.assertEqual(result['wins'],10)

    def test_difference_bootstrap_matches_paired_bootstrap(self):
        baseline=np.array([.1,.2,.4,.6,.8,.3,.1,.2])
        finetuned=np.array([.3,.2,.3,.9,.9,.6,.2,.3])
        result=paired_statistics(baseline,finetuned,resamples=3000,seed=7)
        direct=bootstrap((finetuned-baseline,),np.mean,paired=True,n_resamples=3000,batch=1000,
                         method='BCa',rng=np.random.default_rng(7))
        np.testing.assert_allclose(result['ci95_bca'],[direct.confidence_interval.low,direct.confidence_interval.high],atol=1e-12)
        self.assertEqual((result['wins'],result['ties'],result['losses']),(6,1,1))
        reversed_result=paired_statistics(finetuned,baseline,resamples=3000,seed=7)
        np.testing.assert_allclose(reversed_result['ci95_bca'],[-result['ci95_bca'][1],-result['ci95_bca'][0]],atol=1e-12)

    def test_rejects_unaligned_pairs(self):
        with self.assertRaises(ValueError): paired_statistics([.1,.2],[.3])


if __name__=='__main__': unittest.main()
