# Paired confidence intervals for saved Luna scores

100,000 paired case bootstrap resamples, seed 42, BCa 95% confidence intervals. Each resample keeps baseline and fine-tuned scores from the same case together. No new judging or training.

| Cases | Metric | Mean gain | 95% paired BCa CI | Wins / ties / losses |
| --- | --- | ---: | --- | --- |
| 100 | Source fidelity | +0.130 | [+0.100, +0.156] | 76 / 15 / 9 |
| 100 | Source coverage | +0.095 | [+0.065, +0.122] | 65 / 25 / 10 |
| 80 | Source fidelity | +0.136 | [+0.105, +0.165] | 63 / 9 / 8 |
| 80 | Source coverage | +0.094 | [+0.064, +0.124] | 52 / 19 / 9 |

Both metrics have positive lower bounds in the full-100 and remaining-80 analyses. The conclusion also holds with the supplementary two-metric Bonferroni intervals. The saved scores therefore support a positive average gain and more frequent wins than losses. A confidence interval for the mean does not mean the model improves on every case.

The remaining 80 cases were not used to develop this rubric; all 100 remain development cases. Neither subset is a newly validated clinical test set.

## Scope of uncertainty

- Conditional on the saved judge scores; does not estimate judge rerun variance or systematic judge bias.
- Case bootstrap assumes independent, comparable cases; patient/near-duplicate clustering has not been established.
- For these fixed 100 cases the mean is exact. Intervals concern hypothetical resampling of comparable cases, not uncertainty in the arithmetic.
- All cases are development data. The original 20 informed the rubric; the remaining 80 are a sensitivity analysis, not a new clinical test set.
- No clinical accuracy, clinician calibration or training-seed uncertainty is inferred.

## Reproduce

Use an isolated environment with `requirements-statistics.txt`, then run:

```powershell
.venv/statistics-tools/Scripts/python.exe -m scripts.calculate_paired_confidence_intervals
```

Exact intervals, percentile and paired-t sensitivity checks, two-metric multiplicity adjustment, software versions and input hashes are in `analysis.json`; `summary.csv` contains the main table. The score ledger and paired CSV were cross-checked, and their hashes remain unchanged.

[SciPy paired bootstrap and BCa documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html).
