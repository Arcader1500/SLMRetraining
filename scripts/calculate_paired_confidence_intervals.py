"""Confidence intervals from frozen Luna scores; no model inference or data edits."""
import csv
import hashlib
import json
import math
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import bootstrap, t

from scripts.phase_results import ROOT, read_json

RUN = ROOT / 'results_v3/deepeval_remaining80/judgments/16727c1bd7aaf775'
OUT = ROOT / 'results_v3/paired_confidence_intervals'
METRICS = ('Source fidelity', 'Source coverage')
RESAMPLES = 100_000
SEED = 42


def mean_difference(baseline, finetuned, axis=-1):
    return np.mean(finetuned-baseline, axis=axis)


def paired_statistics(baseline, finetuned, resamples=RESAMPLES, seed=SEED):
    baseline=np.asarray(baseline,dtype=float)
    finetuned=np.asarray(finetuned,dtype=float)
    if baseline.ndim!=1 or baseline.shape!=finetuned.shape or len(baseline)<2:
        raise ValueError('Need at least two aligned one-dimensional case pairs')
    if not np.all(np.isfinite(baseline)) or not np.all(np.isfinite(finetuned)):
        raise ValueError('Nonfinite saved scores')
    delta=finetuned-baseline
    estimate=float(delta.mean())
    if np.ptp(delta)<1e-12:
        bca=percentile=familywise=analytic=[estimate,estimate]
        method='constant paired differences: point interval'
    else:
        result=bootstrap((baseline,finetuned),mean_difference,paired=True,vectorized=True,
                         n_resamples=resamples,batch=1000,confidence_level=.95,
                         method='BCa',rng=np.random.default_rng(seed))
        bca=[float(result.confidence_interval.low),float(result.confidence_interval.high)]
        percentile=[float(x) for x in np.quantile(result.bootstrap_distribution,[.025,.975])]
        # Bonferroni targets nominal >=95% familywise coverage; bootstrap coverage is approximate.
        adjusted=bootstrap((baseline,finetuned),mean_difference,paired=True,vectorized=True,
                           n_resamples=0,bootstrap_result=result,confidence_level=.975,method='BCa')
        familywise=[float(adjusted.confidence_interval.low),float(adjusted.confidence_interval.high)]
        margin=float(t.ppf(.975,len(delta)-1)*np.std(delta,ddof=1)/np.sqrt(len(delta)))
        analytic=[estimate-margin,estimate+margin]
        method='paired BCa bootstrap'
    wins=int(np.sum(delta>1e-12));losses=int(np.sum(delta< -1e-12))
    return dict(cases=len(delta),baseline_mean=float(baseline.mean()),finetuned_mean=float(finetuned.mean()),
                mean_paired_gain=estimate,ci95_bca=bca,ci95_percentile=percentile,ci95_paired_t=analytic,
                ci975_bca_bonferroni_two_metrics=familywise,method=method,
                median_paired_gain=float(np.median(delta)),wins=wins,ties=len(delta)-wins-losses,losses=losses,
                win_fraction_all_cases=wins/len(delta),
                positive_gain_interval=bca[0]>0)


def analyze():
    score_path=RUN/'combined_scores_100.json'
    check_path=RUN/'completion_checks.json'
    manifest_path=RUN.parent.parent/'selection_manifest.json'
    paths=[score_path,check_path,manifest_path,RUN/'combined_summary_100.json',RUN/'combined_paired_comparison_100.csv']
    hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    assert hashlib.sha256(score_path.read_bytes()).hexdigest()==read_json(check_path)['combined_scores_sha256']
    records=read_json(score_path);manifest=read_json(manifest_path)
    summary=read_json(RUN/'combined_summary_100.json')
    assert summary['rubric_version']=='source_grounded_v2' and summary['model']=='gpt-6-luna'
    keyed={(r['case_id'],r['model'],r['metric']):r for r in records}
    ids=sorted(manifest['all_validation_case_ids'])
    expected={(cid,model,metric) for cid in ids for model in ('baseline','finetuned') for metric in METRICS}
    assert len(records)==len(keyed)==400 and set(keyed)==expected
    with (RUN/'combined_paired_comparison_100.csv').open(encoding='utf-8-sig',newline='') as stream:
        csv_rows=list(csv.DictReader(stream))
    assert len(csv_rows)==200 and len({(r['case_id'],r['metric']) for r in csv_rows})==200
    for r in csv_rows:
        for model in ('baseline','finetuned'):
            assert math.isclose(float(r[model]),keyed[(r['case_id'],model,r['metric'])]['score'],abs_tol=1e-12)
        assert math.isclose(float(r['finetuned_minus_baseline']),float(r['finetuned'])-float(r['baseline']),abs_tol=1e-12)
    subsets={'all_100':ids,'remaining_80':sorted(manifest['case_ids'])}
    assert len(ids)==100 and len(subsets['remaining_80'])==80
    assert not set(subsets['remaining_80'])&set(manifest['excluded_case_ids'])
    results={}
    for group,case_ids in subsets.items():
        results[group]={}
        for metric in METRICS:
            b=[keyed[(cid,'baseline',metric)]['score'] for cid in case_ids]
            f=[keyed[(cid,'finetuned',metric)]['score'] for cid in case_ids]
            results[group][metric]=paired_statistics(b,f)
            if group=='all_100':
                assert math.isclose(results[group][metric]['mean_paired_gain'],summary['mean_paired_deltas'][metric],abs_tol=1e-12)
    analysis=dict(method='Paired case-level BCa bootstrap of mean(finetuned-baseline)',
                  confidence_level=.95,resamples=RESAMPLES,seed=SEED,bootstrap_unit='case, with baseline/fine-tuned pairing intact',
                  cross_metric_resampling='Same seed and sorted case IDs use the same resampled case indices for both metrics within each subset.',
                  multiplicity='Main 95% intervals are marginal. Supplementary 97.5% per-metric BCa intervals apply Bonferroni for the two metrics within each subset.',
                  versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
                  input_sha256=hashes,results=results,
                  limitations=[
                    'Conditional on the saved judge scores; does not estimate judge rerun variance or systematic judge bias.',
                    'Case bootstrap assumes independent, comparable cases; patient/near-duplicate clustering has not been established.',
                    'For these fixed 100 cases the mean is exact. Intervals concern hypothetical resampling of comparable cases, not uncertainty in the arithmetic.',
                    'All cases are development data. The original 20 informed the rubric; the remaining 80 are a sensitivity analysis, not a new clinical test set.',
                    'No clinical accuracy, clinician calibration or training-seed uncertainty is inferred.'])
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'analysis.json').write_text(json.dumps(analysis,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    rows=[]
    for group,metrics in results.items():
        for metric,r in metrics.items():
            rows.append(dict(subset=group,metric=metric,cases=r['cases'],mean_paired_gain=r['mean_paired_gain'],
                             lower95=r['ci95_bca'][0],upper95=r['ci95_bca'][1],
                             wins=r['wins'],ties=r['ties'],losses=r['losses']))
    with (OUT/'summary.csv').open('w',newline='',encoding='utf-8-sig') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    lines=['# Paired confidence intervals for saved Luna scores','',
           '100,000 paired case bootstrap resamples, seed 42, BCa 95% confidence intervals. '
           'Each resample keeps baseline and fine-tuned scores from the same case together. No new judging or training.','',
           '| Cases | Metric | Mean gain | 95% paired BCa CI | Wins / ties / losses |',
           '| --- | --- | ---: | --- | --- |']
    for r in rows:
        lines.append(f"| {r['cases']} | {r['metric']} | {r['mean_paired_gain']:+.3f} | [{r['lower95']:+.3f}, {r['upper95']:+.3f}] | {r['wins']} / {r['ties']} / {r['losses']} |")
    positive=all(r['ci975_bca_bonferroni_two_metrics'][0]>0 for group in results.values() for r in group.values())
    conclusion=('Both metrics have positive lower bounds in the full-100 and remaining-80 analyses. '
                'The conclusion also holds with the supplementary two-metric Bonferroni intervals. '
                'The saved scores therefore support a positive average gain and more frequent wins than losses.'
                if positive else 'Some intervals include zero; inspect each metric and subset before concluding that gains are consistently positive.')
    lines += ['',conclusion+' A confidence interval for the mean does not mean the model improves on every case.','',
              'The remaining 80 cases were not used to develop this rubric; all 100 remain development cases. '
              'Neither subset is a newly validated clinical test set.','',
              '## Scope of uncertainty','']
    lines += ['- '+s for s in analysis['limitations']]
    lines += ['','## Reproduce','',
              'Use an isolated environment with `requirements-statistics.txt`, then run:',
              '','```powershell','.venv/statistics-tools/Scripts/python.exe -m scripts.calculate_paired_confidence_intervals','```','',
              'Exact intervals, percentile and paired-t sensitivity checks, two-metric multiplicity adjustment, '
              'software versions and input hashes are in `analysis.json`; `summary.csv` contains the main table. '
              'The score ledger and paired CSV were cross-checked, and their hashes remain unchanged.','',
              '[SciPy paired bootstrap and BCa documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html).']
    (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p.relative_to(ROOT)).replace('\\','/')] for p in paths)
    print(json.dumps(results,indent=2))
    return analysis


if __name__=='__main__': analyze()
