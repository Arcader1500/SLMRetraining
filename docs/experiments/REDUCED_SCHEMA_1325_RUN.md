# Reduced-schema 1,325-example experiment

**Completed 18 November 2026:** the remaining 88 adapter cases were resumed
without retraining, preserving the original 12 predictions and diagnostics.
All 100 cases are scored; the full executed notebook and results are local, and
the T4 runtime has been released. See [SESSION_HANDOFF.md](../SESSION_HANDOFF.md).

This pilot implements the 17 November 2026 handoff's reduced schema before the
5,000-example experiment. The original v2 artifacts remain unchanged.

## Frozen protocol

| Setting | Value |
| --- | --- |
| Prepared version | `e80798edebe5aba5` |
| Training | Same 1,325 cases as v2; projected targets and rebuilt prompts |
| Development | 100 seeded cases from 2,803 eligible validation candidates; previous 30 cases excluded |
| Schema | 30 distinct paths: all ten parents and twenty allowed children |
| Prompt | One extraction instruction; inherited SOAP wording removed |
| Base | `google/gemma-3-270m-it`, revision `ac82b4e820549b854eebf28ce6dedaf9fdfa17b3` |
| Runtime | Colab MCP session `clinical-v3-1325`, Tesla T4, FP32 |
| Generation | Greedy; generated-only repetition penalty **1.08**; maximum 2,048 new tokens |
| LoRA | Rank 16, alpha 32, dropout 0.05; attention and MLP projections |
| Training | Three epochs; batch 1, accumulation 8; learning rate 2e-4; cosine schedule |
| Selection | Minimum development loss; actual choice recorded in training metrics |
| Evaluation | Raw/fence-stripped JSON, allowed keys/types, strict/soft field-aware fact agreement, repetition/budget diagnostics |
| LLM judging | Disabled |

The same stored cases, references, prompts, decoding and comparison contract are
used for baseline and adapter evaluation. Training starts from the original base,
not the v2 adapter. Whole-object parse failures receive zero fact credit. Raw
validity and fence-stripped validity remain separate.

## Local artifacts

- [Preparation and experiment notebooks](../../notebooks/v3_1325): canonical notebooks
  receive actual executed cell outputs; Colab MCP also saves `_output.ipynb`
  snapshots. Preparation through MCP omits execution counts; later notebooks
  executed through nbclient retain real execution counts.
- [Prepared data](../../prepared_clinical_dataset/e80798edebe5aba5): JSONL, DatasetDict,
  manifest, projection audit, rejection log and reference inspection sample.
- [Results](../../results_v3): baseline predictions/diagnostics/scores, adapter and
  training checks/logs, comparison predictions/scores/showcase, execution status.

Per-case outputs are saved during generation. Each completed stage is downloaded
before advancing. The temporary Hugging Face credential file is deleted after
loading; it is excluded from notebooks and archives. The user explicitly approved
dataset/code and credential transfers to this runtime after automatic review
requested destination-specific authorization.

## Data and interpretation limits

All saved rows passed allowed-key/type, complete-sequence length, assistant-mask
and parsed-row digest checks. Normalized exact-note overlap between training and
development is zero. Near duplicates, patient overlap and separation from the
official test split are not established by this pilot. The official test is not
evaluated or used for decisions.

Projection preserves retained values verbatim, drops only newly empty list items,
and preserves separate events even if projection would make them identical. No
projected duplicates were found. Unnamed entries are retained and counted:
training has 29 surgeries, 13 treatments, two tests and one symptom without their
identifier field; development has one surgery and one test without identifiers.

References remain synthetic annotations, not clinician-reviewed gold. Inspection
of the saved training sample still shows weak labels: `train:1482` has vague
"Proper dosage" values; `train:54` asserts two years free of complications despite
the supplied note ending at "freefrom". No clinical claims are repaired or inferred
for this pilot. Scores measure reference agreement, not clinical accuracy.

The new schema, prompt and development cases differ from v2. Cross-version F1
does not isolate improvement. A future 5,000-example run should contain this
training set where quality/leakage rules permit and use the same reduced-schema
evaluation protocol to measure the effect of more data. Equal epochs imply more
optimizer updates at 5,000, so steps, supervised tokens and runtime must accompany
that comparison.


## Completed evaluation

| Metric, same 100 cases | Base | Fine-tuned |
| --- | ---: | ---: |
| Raw-valid JSON | 0/100 | 95/100 |
| Fence-stripped valid JSON | 74/100 | 95/100 |
| Allowed keys and types | 0/100 | 87/100 |
| Mean strict fact F1 | 2.98% | 26.04% |
| Mean soft fact F1 | 5.17% | 41.44% |
| Matched reference facts | 95/2,425 | 657/2,425 |
| Budget hits | 3/100 | 3/100 |

All six code cells in notebook 03 completed with real execution counts and no
cell errors. Local rescoring matches every saved aggregate metric. The original
12 predictions and diagnostics are unchanged. See
[completion_checks.json](../../results_v3/comparison/completion_checks.json).

Five adapter reports fail parsing. Eight additional parseable reports place
keys under disallowed parents; see
[schema_violations.json](../../results_v3/comparison/schema_violations.json).
Thus raw JSON validity and full schema compliance remain distinct.
Fact F1 uses the existing fence-stripped parser; invalid whole objects receive
zero fact credit. No LLM judging or clinical adjudication was added.
