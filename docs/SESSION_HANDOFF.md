# Session handoff: clinical extraction, reduced schema, and 5,000-example experiment

Updated: 18 November 2026. Workspace: `C:/Users/atharva.bedekar/PycharmProjects/SLMRetraining`.

## Latest: all 100 saved validation cases evaluated with the source rubric

**Complete:** the additional 80 cases have all 320 Luna judgments. Combined with
the original 20 source-rubric cases, all 100 saved validation cases have **400
unique measurements**. Source fidelity: baseline 0.386, fine-tuned 0.516, paired
+0.130. Source coverage: baseline 0.407, fine-tuned 0.502, paired +0.095.

Results: `results_v3/deepeval_remaining80/judgments/16727c1bd7aaf775/` contains
`scores.json` (new 320), `summary.json`/`paired_comparison.csv` (new 80 cases),
`combined_scores_100.json`, `combined_summary_100.json`,
`combined_paired_comparison_100.csv` and `completion_checks.json` (all 100).
All keys, frozen inputs, saved flags, original-score hash and combined means/
paired deltas passed verification. Nine offline tests passed. This is LLM source
consistency assessment, not clinician adjudication or exhaustive fact rates.

The first attempt hit a usage limit after 38 saved judgments. The user's
"continue" resumed those exact checkpoints and completed all 282 remaining
judgments without repeating saved keys. The process has exited. Progress files
now say complete, 320 saved, zero pending; no refill or further inference is
needed for this evaluation. Original source-20 and reference-only scores remain
unchanged. Gemini stayed disabled. No training or extraction inference ran.

`docs/REMAINING_VALIDATION_EVALUATION.md` has results and resume details. The HTML
still documents the earlier completed 20-case evaluation; it has not yet been
expanded to show these full-100 results. The training audit remains at its
initial ten-case pilot; do not confuse that with this completed validation run.

## Historical launch instructions: evaluate remaining 80 validation cases

The user explicitly requested completing the unchanged source-grounded rubric on
the other 80 of the 100 frozen validation cases: **320 new judgments** (80 cases,
baseline and fine-tuned, Source fidelity and Source coverage). Model stays
`gpt-6-luna`; Gemini remains disabled. Training-label audit work is separate and
must not replace this active task. No training, regeneration or label changes.

The remaining batch is prepared in `results_v3/deepeval_remaining80/`. Its 80 IDs
are the exact complement of the original 20, with no filtering or resampling.
Read `docs/REMAINING_VALIDATION_EVALUATION.md` and the batch's `progress.json` for
current progress. Do not infer completion from this handoff's launch description.

Start/resume from repository root:

```powershell
.venv/deepeval-tools/Scripts/python.exe -u -m scripts.run_deepeval --remaining-validation --source-grounded --run --backend codex
```

User authorization persists across interruptions and refills. The same command
reuses the immutable selection/rubric and skips every completed key. Each score
and reason is flushed/atomically checkpointed immediately; `.pending` is not an
accepted score. Progress mirrors saved/remaining counts, complete cases and
current/pending keys. On quota/provider failure it stops without scoring zero or
retrying in a loop. Restart after access returns. An OS lock prevents concurrent
writers and releases on exit/crash; do not delete score files to resume. Forced
termination can leave status `running`; check the process and trust `scores.json`
as authoritative. There is no automatic refill scheduling.

All nine offline tests passed, including simulated quota interruption after
three judgments and resume with no repeated completed measurements. The real
run was launched in this session; inspect progress for the latest saved count.
Original 20-case source scores (`d44ef976ae8d9310`) and reference-only scores
(`a6bb10a9fde5e2b4`) are preserved. The source rubric text is unchanged. Runner and
adapter code now have checkpoint/limit handling; historical code hashes in older
provenance naturally differ from the current implementation. Do not confuse
that with modified clinical inputs or old scores.

After all 320 new judgments, the runner writes the 80-case summary/paired CSV and
combines the original 80 source-rubric measurements with these 320 into
`combined_scores_100.json` and `combined_summary_100.json` (100 cases, 400 total).
Do not include the reference-only rubric in that aggregate. The existing HTML
still documents completed 20-case results; do not call partial results complete.
The user's no-code-review preference remains in effect.

## Training-label audit started; initial ten-case pilot reviewed

The user agreed to start a training-data audit. Saved work is in
`results_v3/training_audit_100/`; read its `REPORT.md` and `README.md` first.
**The full 100-case semantic audit is not complete.** The frozen sample has 50
random and 50 targeted training cases; the initial five from each arm have
GPT-6 Luna candidate reviews and assistant source review. No judge process is
currently running; 90 cases remain. Gemini stayed disabled. No training,
replacement labels, synthetic notes or extraction generations were produced.

Structural checks cover all 1,325 training rows: schema/masks consistent, unique
normalized notes, no exact overlap with current development cases or duplicate
projected array entries. 1,206 lack terminal punctuation; this is a screening cue,
not a confirmed count of truncated notes. Sample hashes and source quotes checked.

Important new diagnosis: every current label exactly matches literal v2 schema
projection. This drops v2 treatment frequency (418 fields across 285 cases),
duration (311 across 240), and diagnostic condition (1,624 across 1,034), among
other fields. These are mechanical drops, not clinical error rates. Source review
confirmed lost schedules in train:119/1239/1453, seven-day therapy in train:1052,
and final ectopic-pancreas diagnosis/margin status in train:177. Some important
content could be retained within existing dosage/time/result/details strings;
no mapping or label repair has been implemented yet. Do not add schema paths.

Pilot judge run: `judgments/e1a7efa71d6b7cf2/`, instructions and response schema
frozen in its contract. Of 17 candidate findings, assistant review confirms six,
downgrades six to policy ambiguity and rejects five. Five additional omissions
were found during review: 11 diagnostic findings across eight cases, not
prevalence/atomic error rates. Some judge flags describe supported facts as errors;
calibrate before scaling. `pilot_adjudications.json` preserves all dispositions.
One excerpt's unique source token span was recovered after parentheses-only quote
mismatch; raw rejected evidence and repair records remain saved. This is not
prediction/label repair. Source consistency does not establish medical truth.

Scripts: `audit_training_data.py` prepares sample without inference, and explicit
`--run --limit 10` executes the pilot. Larger limits make additional calls.
`analyze_training_projection.py` verifies all v3 labels against v2 and counts
dropped fields. `review_initial_pilot.py` under the audit folder rebuilds reviewed
sidecars. `docs/CLINICAL_ANNOTATION_POLICY.md` is the initial policy; instructions
are snapshotted so future edits create another judge contract. Three focused
offline tests passed. Original training data remains unchanged.

Next: clarify broad history-field semantics, calibrate the auditor, define
source-verified semantic folding within the existing 30 paths, then continue
the remaining 90 source reviews before constructing versioned replacement labels.
The user's no-code-review preference remains in effect.

## Source-grounded reevaluation completed

The user authorized rerunning both saved models on the same 20 cases and the same
two fidelity/coverage dimensions, with the clinical note now authoritative.
**All 80 real GPT-6 Luna judgments completed.** Source fidelity is baseline 0.355,
fine-tuned 0.460 (paired +0.105); source coverage is 0.370 versus 0.470 (+0.100).
Each metric has 13 fine-tuned wins, six ties and one loss. Gemini stayed disabled.
No extraction generations, training, model changes or frozen reference repairs.

New rubric: `scripts/source_grounded_rubric.py`, version `source_grounded_v2`.
`scripts/run_deepeval.py --source-grounded --run --backend codex` explicitly sends
input note, actual output and expected reference. The default retains the old
rubric. New results are in `results_v3/deepeval_20/judgments/d44ef976ae8d9310/`;
old `a6bb10a9fde5e2b4` scores remain unchanged. New scores/reasons, paired CSV,
summary, contract, provenance, completion checks and judge quality notes are saved.

`docs/Clinical_Extraction_Phases_1_and_2.html` is rebuilt with both rubric runs,
source-grounded results first, full rubrics and per-case scores/reasons. It
explicitly separates between-rubric assessment changes from model improvements.
Read `docs/SOURCE_GROUNDED_REEVALUATION.md` for results, execution and limitations.
Source-note access has not eliminated judge mistakes: `quality_notes.json` records
two evidence-checked misreadings of references, with scores unmodified. Some
fidelity reasons also discuss omissions despite coverage having that role. No
clinician calibration or exhaustive claim-level precision/recall is claimed.

Verification: `scripts/check_source_grounded_evaluation.py` passed all 80 keys,
means/deltas, frozen hashes, original-score preservation and saved format flags.
Six offline tests passed. Headless desktop/mobile Chrome checks passed both
rubric tables and case reasons with no page errors or external requests. Original
notebook outputs still document the original reference-only run; the reevaluation
ran through the CLI, as recorded in its separate provenance. No code-review
workflow was used, honoring the user's preference.

## Source-grounded 20-case audit complete

Completed 18 November 2026. Read `results_v3/source_audit_20/REPORT.md` for
interpretation and next experiments, and `CASE_LEDGER.md` for all case evidence.
`audit.json` resolves source quote offsets and model/reference evidence;
`probes.csv`, `findings.csv`, `reference_and_judge_concerns.csv` and
`field_outcomes.csv` provide exports. Original 12-case `annotations.json` remains
unchanged; completed annotations are in `reviewed_annotations.json`.

The completed diagnostic audit has 160 probes (40 demographic, 120 clinical),
104 model findings (51 baseline, 53 fine-tuned), 23 reference concerns across
18 cases and 29 judge concerns across 18 cases. Clinical supported probes rise
46 to 60; omissions fall 50 to 35; wrong-value/relation probes rise 6 to 14.
These are selected diagnostic probes, not exhaustive precision/recall or error
rates. Reference concerns separate three clear discrepancies, six omissions,
one annotation-policy issue and thirteen temporal/causal ambiguities.

All 20 raw outputs and sources were inspected, including malformed prefixes and
arrays. Earlier labels and two overstated draft judge criticisms were reconciled;
see `reconciliation_log.json`. Source quote/evidence checks, frozen paired-data
hash and ten upstream source hashes passed; `validation_checks.json` records
provenance. This is assistant source-consistency review, not clinical adjudication.
Rebuild with workspace Python: `complete_annotations.py`, then `build_report.py`,
both under `results_v3/source_audit_20/`.

No inference, training, model changes or frozen reference/score changes occurred.
Gemini remains disabled. Next experiments are proposals only: clarify annotation
policy, review separate training labels, isolate label quality, then data size,
model capacity and rank. Do not train on these 20 development cases. The user's
no-code-review preference remains in effect.

## Historical handoff: finish the source-grounded 20-case audit (superseded)

**The user requested this handoff and will start a fresh chat. Stop work here.**
The next task is to finish the audit, then propose controlled next experiments.
The audit is incomplete; do not describe it as a completed assessment.

The user questioned the modest DeepEval gain and lack of actionable diagnosis.
They approved auditing all 20 selected cases against the supplied notes, covering
both baseline and fine-tuned outputs and separating model errors, reference
problems and judge mistakes. No new judge inference is needed. Gemini remains
**disabled**. Do not run training or change models merely because next-step
options were discussed. The user's no-code-review preference still applies.

Saved work: `results_v3/source_audit_20/`:

- **Read `README.md` first** for annotation syntax, provisional status labels,
  index limitations and the exact remaining work.
- `annotations.json`: 12 draft case reviews, **96 fact probes**, **61 model
  findings**, 15 reference concerns and 15 judge concerns. All counts are draft
  ledger sizes, not exhaustive error rates or clinician-confirmed defect counts.
- `indexed_inputs.json`: all 20 source notes and indexed reference/model leaves.
- `progress.json`: completed-draft IDs and remaining IDs. All currently saved
  source quotes passed exact substring checks; semantic labels still need review.
- Original notes, references and full outputs:
  `results_v3/deepeval_20/paired_cases.json`. Frozen selection/source hashes:
  `results_v3/deepeval_20/selection_manifest.json`. Judge reasons remain in
  `results_v3/deepeval_20/judgments/a6bb10a9fde5e2b4/scores.json`.

**Eight cases still need saved reviews:** `validation:412`, `validation:2654`,
`validation:1133`, `validation:1628`, `validation:1722`, `validation:2890`,
`validation:435`, `validation:337`. The first four were read but not annotated
before interruption; re-read them rather than assuming completion.

Important audit pitfalls and verified examples:

- Unparsed-output scalar indexing misses array strings and unfinished quoted
  text. Baseline 2654 copies most of the note into an unclosed `visit motivation`
  string and has zero indexed leaves: readable facts are present. Baseline 1388
  includes seizures in arrays; baseline 2890 includes long source excerpts in
  arrays. Always inspect the original raw text before marking omissions.
- Case 302: true drug/dose and adverse-response mixing. Dosulepin's 150 mg dose
  and sweating are given to methysergide; amitriptyline dose becomes Dopamine.
  But depressive-disorder history is source-supported despite being absent from
  the reference history, and mirtazapine details survive under symptom details.
- Case 128: a refused CT-guided biopsy is assigned VATS tissue-staining results;
  Mucine oil is invented. Some unnamed local-clinic medication really is stated,
  despite the reference's empty treatments.
- Case 1241: afebrile after 48 hours becomes five weeks; TMP/SMX dose becomes other
  antibiotic names. The reference's discharge summary is not supported by an
  explicit disposition in the visibly truncated source.
- Judge false criticisms verified in notes: welding occupation in 1351,
  parking-lot second seizure in 1388, neglect/violence and family history in 725,
  and operative details in 2654 are source-supported. Reference-only penalties
  must not be relabeled clinical hallucinations.
- In the inspected but unsaved case 412, fine-tuned F07's uneventful course,
  improved ambulation and collar are explicitly supported. ICU admission for halo
  traction is also explicit. The judge calls these unsupported/misstated. Actual
  errors include MRI/CT result mixing, halo-vest response assigned to traction,
  weakness timed before the accident, and missing revision surgery. Baseline
  turns denied dysphagia positive and gives a halo-vest a 100 mg dose.
- In inspected but unsaved 1133, the source explicitly states four transfusions;
  do not repeat the judge's invented-transfusion criticism. Baseline mixes three
  hospitalizations with four transfusions. Fine-tuned output calls a root stump
  surgery and loops electrophoresis until truncation.
- In inspected but unsaved 1628, another hospital deemed the patient inoperable,
  followed by a decision for surgery at the current hospital. Fine-tuned output
  wrongly asserts the later surgery was already performed at an 11-year interval
  and mixes the earlier inoperability into its treatment reaction. The reference
  also lists generic Surgery as treatment before a performed procedure is shown.

Next deliverables: finish and verify all 20 reviews; produce source-quote-backed
JSON/CSV and a readable audit report with counts by clinical field/error category,
plus actionable data/annotation priorities. Use explicit diagnostic probes; do
not imply exhaustive atomic-fact precision/recall without a full claim inventory.
No formatter/validator or final audit report exists yet. Preserve all original
artifacts and keep audit evidence outside the 30-path output schema.

### Model/rank discussion while the audit was active

The user asked when to change LoRA type/rank and whether to move to ~0.5B. No new
experiment was authorized or started. Recommendation discussed:

1. Finish the audit and address training-label/annotation-policy problems first.
2. Test a ~0.5B base with ordinary LoRA **r=16** before changing adapter type.
   Concrete candidates verified from publisher cards: Qwen2.5-0.5B-Instruct;
   Qwen3-0.6B if slightly above 0.5B is acceptable. Neither is proven better here.
3. Compare each model with its own base baseline on the same held-out cases and
   semantic instruction, using its own chat template/tokenization. Record model
   family/pretraining differences and recheck longest-row GPU memory; do not
   assume T4 fit from parameter count alone.
4. If clean training examples remain hard to fit, try **r=32** as a separate
   experiment. Keep standard LoRA alpha/r scaling consistent (e.g. r16/alpha32
   versus r32/alpha64) if testing rank alone. DoRA/other variants can wait for
   evidence that plain LoRA is limiting learning.
5. Do not train on the audited 20 development cases or silently repair frozen
   evaluation references. New targeted training examples must come from separate
   training cases; reference corrections require a separately versioned protocol.

Primary references consulted for this discussion:
[Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct),
[Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B),
[PEFT LoRA configuration](https://huggingface.co/docs/peft/package_reference/lora).

The sections below retain experiment history. The active task above takes
precedence over older instructions to launch a 5,000-example run.

## Current status: reduced-schema pilot completed (18 November 2026)

The user resumed the remaining 88 cases on 18 November. **All 100 adapter
predictions and the complete comparison are saved locally.** The original 12
predictions and diagnostics were preserved unchanged. The Colab T4 runtime
`clinical-v3-1325` has been stopped after download and local verification.
This status supersedes historical statements below that v3 has not been created.

| Metric, 100 matched development cases | Base | Fine-tuned v3 |
| --- | ---: | ---: |
| Raw-valid JSON | 0/100 | 95/100 |
| Valid after fence removal | 74/100 | 95/100 |
| Exact ten top-level fields | 0/100 | 95/100 |
| Allowed keys and types throughout | 0/100 | 87/100 |
| Mean strict fact F1 | 2.98% | 26.04% |
| Mean soft fact F1 | 5.17% | 41.44% |
| Matched reference facts | 95/2,425 | 657/2,425 |
| Token-budget hits | 3/100 | 3/100 |

- Prepared dataset: `prepared_clinical_dataset/e80798edebe5aba5/`; exact 30-path
  schema, 1,325 training cases, 100 development cases, one coherent prompt.
- Frozen inference: FP32/T4, greedy, generated-only repetition penalty **1.08**,
  maximum 2,048 new tokens. Runtime torch remains `2.14.1+cu130` across the resume.
- Training completed previously: three epochs, 498 steps, 39.4 minutes.
  Development losses 0.485237 -> 0.456911 -> 0.451426; checkpoint 498 selected.
  Adapter: `results_v3/finetuned_v3/adapter/`; all 252 saved tensors checked finite.
- Baseline artifacts: `results_v3/baseline/`. Full comparison, per-case CSV,
  generations, diagnostics, showcase and aggregate scores: `results_v3/comparison/`.
  `completion_checks.json` records successful local rescoring, all 100 case IDs,
  unchanged cached 12 outputs/diagnostics and error-free completed notebook cells.
- Canonical notebooks in `notebooks/v3_1325/` have local executed cell outputs.
  Notebook 03 and its `_output.ipynb` snapshot now both mark execution complete.
- Eight parseable adapter outputs violate the schema by placing keys under the
  wrong parent (e.g. `surgeries.result`, `treatments.result`, or treatment keys
  under examinations). Five outputs fail whole-object parsing. Details are in
  `results_v3/comparison/schema_violations.json`. Do not equate 95 valid JSON
  objects with 95 schema-compliant reports. Invalid whole objects get zero fact
  credit; fact scores otherwise use the established fence-stripped evaluator.
- No LLM judging or clinical adjudication was performed. Scores measure agreement
  with imperfect synthetic references. No code-review workflow should be invoked
  for these fine-tuning iterations, per the user's explicit instruction.
- The 5,000-example experiment has not started. Preserve the revised schema,
  prompts, evaluation cases and decoding for a data-size comparator. v2 is intact.

Operational notes for future Colab runs:

- Restore results under **`/content/results_v3`** because notebook outputs use that
  absolute root; keep prepared data/helpers under `/content/clinical_v3` and run
  from that workspace. The initial resume restored results under the workspace;
  this was corrected before the successful resumed generation.
- MCP `exec_file` has a five-minute transport timeout even if a longer execution
  timeout is passed. Use `scripts/run_colab_notebook.py` in a background process
  launched via Colab MCP. It uses nbclient and saves real outputs after completed
  cells. Download executed notebooks inside ZIP files: direct MCP notebook
  download serializes notebook content as Python repr instead of JSON bytes.
- Source data/code and a Hugging Face read-token transfer to the Colab experiment
  were explicitly approved previously. Temporary token files were deleted after
  loading and excluded from experiment archives and notebooks.

Protocol and interpretation limits: [REDUCED_SCHEMA_1325_RUN.md](REDUCED_SCHEMA_1325_RUN.md).
Machine-readable status: `results_v3/experiment_status.json`.

## Latest: real Codex DeepEval completed with GPT-6 Luna

The user explicitly requested running the frozen 20-case evaluation with
**`gpt-6-luna`**, correcting the prepared `gpt-6.1-sol` setting. The real run is
complete: 20 cases, 40 baseline/fine-tuned output/reference comparisons, two
metrics per output, **80 saved judgments**. Gemini stayed disabled; no Gemini
or API-key judge calls were made. Codex used the existing ChatGPT-authenticated
CLI. No Colab runtime was required.

Mean reference fidelity: baseline **0.335**, fine-tuned **0.375** (paired +0.040).
Mean reference coverage: baseline **0.410**, fine-tuned **0.455** (+0.045).
These semantic gains are modest compared with the formatting gains. Scores
measure synthetic-reference agreement, not clinical accuracy or validated judge
reliability. No token-probability normalization is available through the CLI.

- Results/reasons/paired CSV/summary/contract/checks:
  `results_v3/deepeval_20/judgments/a6bb10a9fde5e2b4/`.
- Executed canonical notebook and `_output` snapshot:
  `notebooks/v3_1325/04_deepeval_paired_20.ipynb` and its `_output.ipynb` sibling.
- Status/provenance: `results_v3/deepeval_20/notebook_execution.json` and
  `execution_provenance.json`.
- `judge_settings.json` has the Codex model `gpt-6-luna` and execution enabled;
  Gemini remains `enabled=false`. Never enable Gemini automatically after Codex.
- The same 20 IDs and raw outputs were retained, including three raw-invalid
  fine-tuned outputs. All 80 keys are unique; mean scores and paired deltas were
  recomputed locally. Notebook execution has no error outputs.
- The combined HTML visualizer now includes these Codex scores. Desktop/mobile
  browser checks passed with no page errors or external requests.
- The preparation-only status in the historical section below and in the frozen
  selection manifest describes the earlier preparation state, not current status.

## Visualizer and planned DeepEval evaluation (18 November 2026)

A new standalone report, `docs/Clinical_Extraction_Phases_1_and_2.html`, combines
phase 1 (cleaned v2, 30 development cases) and phase 2 (reduced v3, 100 cases).
It embeds actual summaries, loss logs, all 130 case outputs and a 20-case sample
selector. It explicitly marks the phases as different protocols/evaluation sets;
cross-phase F1 is not a controlled schema/data-size improvement. Original HTML is
preserved. Rebuild with `python -m scripts.build_phase_visualizer`.

The user requested **preparation only** for DeepEval. A frozen seed-42 selection
in `results_v3/deepeval_20/` contains the same 20 phase-2 cases for baseline and
fine-tuned comparison against dataset references (40 comparisons; two metrics,
80 planned metric measurements). No validity/score filtering; three selected
fine-tuned outputs are raw-invalid. All original outputs remain verbatim.

Judge setup: **Codex CLI is the default; Gemini is disabled and must only be
used after a completed Codex run.** Current Codex model configuration is
`gpt-6.1-sol` (editable before execution); Gemini is `gemini-3.8-flash`.
No real judge calls were made. `run_judge=false` and notebook `RUN_JUDGE=False`.
No automatic fallback. Notebook `notebooks/v3_1325/04_deepeval_paired_20.ipynb`
has executed preparation-cell outputs. Requirements and dependencies are isolated
from training (`requirements-deepeval.txt`; locally `.venv/deepeval-tools/`).

Use `docs/DEEP_EVAL_PAIRED_20.md` for execution switches, environment credentials,
source hashes, scoring limits and results layout. Custom Codex integration uses
`codex exec` with saved CLI authentication, not subscription-token API emulation;
CLI logprobs are unavailable, unlike native G-Eval normalization. Gemini requires
explicit enabling and `GOOGLE_API_KEY` in the kernel/process environment, after
Codex completion. The current CLI reports ChatGPT sign-in. Read-only CLI checks
and offline stub compatibility tests consumed no model inference.

Verification: five focused offline tests passed; headless Chrome checks covered
phase/decoding controls, 130 case outputs, the 20-case selector, parse-failure
filters, loss toggle and a 390px mobile viewport, with no JS errors or external
requests. No code-review workflow was used. The latest user preference continues
to prohibit code review for fine-tuning iterations.

## 1. User objective and latest direction

The goal is to demonstrate useful fine-tuning of a small model with a reproducible before/after comparison. SOAP summarization is not a requirement. The current task extracts facts from clinical notes into structured JSON. The user wants to continue this direction with approximately **5,000 accepted training examples** and a smaller output schema, while retaining **all ten existing top-level sections**.

The user requested a subset of about 20?30 keys, never more, and explicitly prohibited cutting parent keys. We use the conservative counting rule **30 distinct schema paths in total: ten parents plus twenty child paths**. Repetition of a field in different array entries does not add a new schema path; actual per-report key occurrences can exceed thirty. The user prefers field descriptions as text or a table, rather than a nested Markdown field list.

The original audit recorded the schema recommendation before implementation. The 1,325-example v3 pilot is now complete as summarized above; the 5,000-example experiment remains a future phase. Keep existing v1/v2 data, adapters, contracts, and results intact.

## 2. What dataset was actually used

Source: [AmareshHebbar/clinical-summarizer-sft](https://huggingface.co/datasets/AmareshHebbar/clinical-summarizer-sft), pinned revision `4ca20e0a38cc9235045c973b5503d49952fd1fac`. It provides 24,000 training, 3,000 validation, and 3,000 test records.

The dataset card advertises SOAP summaries and shows a four-section example, but its actual assistant answers contain the ten-section JSON used in this repository. The source system message also asks for SOAP despite these JSON targets. Preparation reads `messages` from this dataset, takes the original assistant answer, and cleans it. It does not load an upstream `summary` column or accidentally select another dataset.

During exploration, all **1,325 saved training examples** were compared with their original records from the pinned revision. Original message hashes, clinical notes, and outputs after v2 cleaning match. All **30 saved validation examples** were also checked against original source message hashes and notes.

The card identifies [AGBonnet/augmented-clinical-notes](https://huggingface.co/datasets/AGBonnet/augmented-clinical-notes) as upstream. That upstream card documents GPT-4-generated structured summaries from clinical case notes and GPT-3.5-generated dialogues. The downstream card's claim of no synthetic content conflicts with this provenance. Treat references as synthetic annotations needing source review, not independently verified clinical gold labels. Distinguish the published clinical notes from generated annotations/dialogues.

Important prompt defect: current v2 preparation appends explicit JSON extraction instructions to the inherited SOAP system text. The new experiment should replace the contradictory instruction with one coherent extraction instruction, applied identically during training and evaluation. Record this as a new prompt/protocol version.

## 3. Current cleaning and dataset sizes

Authoritative implementation: [scripts/prepare_v2_dataset.py](../scripts/prepare_v2_dataset.py). Saved v2 manifest: [manifest.json](../prepared_clinical_dataset/eeff5efa1619f198/manifest.json).

Preparation scans the first **1,500 candidate training records**, not the full training split. It rejects 68, keeps 1,432 before cross-split filtering, and excludes another 107 because their normalized notes appear in the eligible validation pool. Final training size is **1,325**. It scans all 3,000 validation records, obtains an eligible pool of 2,834, and samples 30 with seed 42. The current workflow does not use the official test split.

Current cleaning/preparation:

1. Require a single nonempty system/user/assistant conversation; the `model` answer-role alias is also accepted.
2. Parse an object with exactly the ten expected top-level keys. Strip enclosing Markdown fences and conservatively escape unescaped control characters. Reject duplicate JSON keys, NaN/Infinity, unresolved JSON syntax, invalid section types, and targets without nonmissing content. Do not guess missing medical facts or repair syntax with an LLM.
3. Recursively remove missing leaves: JSON null and case/whitespace-normalized strings matching empty text, none, null, unknown, or not provided. This exact list does not catch every verbose placeholder, such as ?Outcome not specified.?
4. Keep `visit motivation` as a scalar string, using ?None? when absent. Keep patient information/history/discharge as objects and the six remaining sections as arrays. Empty sections are `{}` or `[]`. A dict supplied for an array section is wrapped as one item. Drop empty dummy entries and deduplicate exact cleaned array entries in order.
5. Deduplicate notes using case/whitespace normalization within splits and exclude training notes appearing anywhere in the eligible validation pool. This does not detect all paraphrases or patient overlap, and does not establish separation from the official test set.
6. Add the extraction instruction, apply the pinned model chat template, and tokenize with no extra special-token insertion. Mask prompt labels with -100; supervise the complete assistant answer and closing tokens. Reject complete sequences longer than 4,096 tokens; do not truncate or pack.
7. Save source identity/hashes, notes, references, prompts, text, token IDs, attention masks, labels, logs, manifests and a Hugging Face DatasetDict.

The original-style saved v1 targets average 88.4 total key occurrences per example; cleaned v2 targets average 45.4. Both always have ten parents. These figures describe the same 1,325 retained training cases, not all raw records. V2 training sequences average 1,055.3 tokens, maximum 1,651, with mean 487.7 supervised tokens.

Observed retention is 88.3%. Extrapolating that rate to 24,000 candidates gives approximately 21,200 usable examples. This is an estimate only; the first 1,500 need not be representative, and new filtering/schema rules change retention. About 5,660 candidates would be needed to obtain 5,000 at that rate, but the next phase should inspect/sample the full candidate pool rather than assume a fixed prefix is sufficient.

Cleaning removes syntax/scaffolding defects. It does not validate clinical correctness or restore source text already missing from the downloaded note.

## 4. Active pipeline and frozen artifacts

The primary workflow is the three Colab notebooks, not the separate CLI package:

| Stage | Existing implementation / artifact |
| --- | --- |
| Prepare v2 | [scripts/prepare_v2_dataset.py](../scripts/prepare_v2_dataset.py) |
| Base-model baseline and frozen contract | [notebooks/01_baseline_eval.ipynb](../notebooks/01_baseline_eval.ipynb), [results_v2/baseline/](../results_v2/baseline/) |
| Fine-tune | [notebooks/02_finetune.ipynb](../notebooks/02_finetune.ipynb), [results_v2/finetuned_v2/](../results_v2/finetuned_v2/) |
| Adapter evaluation and comparison | [notebooks/03_eval_and_compare.ipynb](../notebooks/03_eval_and_compare.ipynb), [results_v2/comparison/](../results_v2/comparison/) |
| Current frozen data | [prepared_clinical_dataset/eeff5efa1619f198/](../prepared_clinical_dataset/eeff5efa1619f198/) |
| Detailed old-run briefing | [TRAINING_AND_EVAL_BRIEFING.md](TRAINING_AND_EVAL_BRIEFING.md) |
| Source-grounding audit | [EXTRACTION_AUDIT_2026-11-17.md](EXTRACTION_AUDIT_2026-11-17.md) |

V1 data version is `900825a06d38a006`; v2 is `eeff5efa1619f198`. The v2 train and validation hashes are `f3bc7f7bfdc3fbecdefab6e238c85a75dec66548e50a127f8297e6364a808340` and `5a5f86399b90ade85a1d3aab5569899593d3e428c97bb2b758b09adb12e34724`.

These are **canonical parsed-row digests**, computed as SHA-256 of JSON-serialized rows with sorted keys and Unicode preserved, not hashes of JSONL file bytes. Do not report a file-byte mismatch as data corruption. Contracts also freeze case IDs, prompt digest, model revision, decoding, and recorded versions.

The [clinical_sft/](../clinical_sft/) CLI package, [CLINICAL_PIPELINE.md](CLINICAL_PIPELINE.md), and [requirements-clinical.txt](../requirements-clinical.txt) describe a separate artifact/protocol format. Do not interchange its prepared data with the notebook data. Historical pilots and notebooks live under [archive/](../archive/); the prior handoff described that earlier phase and is superseded by this document.

## 5. Model, completed training, and results

Base model: **google/gemma-3-270m-it**, approximately 270M parameters, revision `ac82b4e820549b854eebf28ce6dedaf9fdfa17b3`. Training and inference used FP32 on a Colab Tesla T4. Avoid FP16 as a T4 fallback; numerical overflow was a problem in the earlier workflow. Native BF16 is a separate hardware/protocol choice, not an automatic equivalent comparison.

Completed v2 recipe: LoRA rank 16, alpha 32, dropout 0.05 on q/k/v/o and gate/up/down projections; batch 1, accumulation 8; learning rate 2e-4, cosine schedule, warmup 0.08, weight decay 0.01, gradient clipping 1.0. Three epochs yielded 498 optimizer steps. Gradient checkpointing was disabled after the longest-row backward check fit at 8.338 GiB. Epoch-end validation/checkpoints selected checkpoint 498 by minimum validation loss 0.511892. Training took approximately 40.3 minutes. Declining loss across three epochs does not prove absence of overfitting or reliable free generation.

Observed runtime versions: transformers 4.57.6, peft 0.18.1, datasets 4.8.5, accelerate 1.15.0, torch 2.14.1+cu130. Notebook installation cells pin some packages and range-pin others; these are recorded runtime versions, not a fully pinned lockfile. Project pyproject.toml/uv.lock describe a newer different stack. Do not blindly uv-sync that stack for reproduction. Exact old contracts assert versions, including torch; investigate deliberate environment changes rather than deleting those guards silently.

Both baseline and adapter were evaluated on the same 30 cases with FP32, greedy generation, and max_new_tokens 2048. Two conditions were pure greedy `rp_1.00` and generated-only repetition penalty `gen_rp_1.08`. The latter penalizes previously generated tokens while excluding prompt-only tokens from the penalty history.

| Model / decoding | Raw-valid JSON | Fence-stripped valid | Exact 10 parent keys | Mean strict F1 | Mean soft F1 | Budget hits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Base / greedy | 0/30 | 6/30 | 0/30 | 0.51% | 0.87% | 10/30 |
| Base / generated-only 1.08 | 0/30 | 22/30 | 0/30 | 0.49% | 2.09% | 2/30 |
| Fine-tuned / greedy | 25/30 | 25/30 | 25/30 | 18.02% | 29.61% | 3/30 |
| Fine-tuned / generated-only 1.08 | 28/30 | 28/30 | 28/30 | 18.93% | 30.74% | 2/30 |

Matched facts rose from 4 to 198 of 1,082 reference facts under generated-only 1.08. All nested key paths match in 0/30 even after fine-tuning; this differs from matching the ten top-level keys. Scores measure agreement with synthetic references, not clinical accuracy.

## 6. Exploration and semantic audit findings

[The detailed audit](EXTRACTION_AUDIT_2026-11-17.md) reviews all 30 best-condition predictions against notes and references. It is assistant source-consistency review, not clinician adjudication or exhaustive atomic-fact annotation. Baseline predictions were not separately clinically adjudicated.

Age and sex agree after normalization in 30/30 outputs, including readable prefixes of the two malformed outputs. All 30 reports nevertheless need at least one source-grounding, field, or event-assignment correction; severity varies. Examples include reversing antibiotic susceptibility in case 922, inventing treatment schedules in 2761, adding explicitly absent facial paralysis in 2538, and mixing distinct admissions/drug timelines. These are not explained only by strict paraphrase scoring.

At least 7 references contain clear defects; e.g. case 362 assigns a prior dengue stay to the current weakness admission, and 1175 stores 14 years of follow-up as admission duration. At least 28 supplied notes visibly end mid-word/phrase/sentence; original-source matching confirms these cutoffs predate our preparation. Do not infer an unsupported continuation. A complete note would require an explicitly versioned upstream-source change, not silent text replacement.

Conclusion: this run demonstrates useful learning but current reports need correction. Neither a reliable clinical product nor a Gemma 270M capability limit is established. More clean diverse data could help; gains from increasing data have not been measured. The current user prefers moderate schema reduction plus a 5,000-example experiment over abandoning all ten sections for symptom-only extraction.

Alternative dataset ruled out: [stindardlogic/medical-clinical-reasoning-sft-100k](https://huggingface.co/datasets/stindardlogic/medical-clinical-reasoning-sft-100k), revision `c01f314cb453876617c407cad1c8557be2a5d09e`. A full 655,694,817-byte scan found 100,000 rows but only 15 distinct prompts, 15 answers, and 15 prompt-answer pairs, each repeated 6,666?6,667 times. It is synthetic, broad, and verbose. A random row split would leak identical content. Evidence: [dataset_candidate_audit_2026-11-17.json](dataset_candidate_audit_2026-11-17.json). Do not switch to that revision for a generalization demonstration.

## 7. Recommended reduced schema: exactly 30 paths

A user-requested **gpt-6.1-sol** subagent independently analyzed the saved training/validation data and semantic audit. Detailed measurements, field coverage, hashes, projection behavior, and limitations are in [schema_reduction_analysis_2026-11-17.json](schema_reduction_analysis_2026-11-17.json). The recommendation was accepted for this handoff; it is not yet implemented in preparation or notebooks. The observed original schema contains 57 child paths, or 67 paths including parents; the proposed schema retains 20 of those child paths.

| Parent, preserved with original type | Retained child keys, exact spelling | Child count |
| --- | --- | ---: |
| visit motivation, string | No children; retain scalar | 0 |
| admission, array | reason | 1 |
| patient information, object | age; sex | 2 |
| patient medical history, object | physiological context | 1 |
| surgeries, array | Type; time; details | 3 |
| symptoms, array | name of symptom; location; time; details | 4 |
| medical examinations, array | name; result | 2 |
| diagnosis tests, array | test; result | 2 |
| treatments, array | name; dosage; time; reaction to treatment | 4 |
| discharge, object | discharge summary | 1 |
| Total | Ten parents plus twenty children | 20 |

Rationale: retain clinical episode coverage, basic demographics, main history, symptom location/timing/context, named investigations with results, procedure specifics, treatment identity/dose/timing/response, and discharge narrative. Keep symptoms.details to preserve context/negation often absent from the symptom name; keep surgeries.details to avoid reducing surgery to a generic label. These fields remain potentially verbose and require source review.

Drop low-coverage demographic/lifestyle fields, duplicated explanations, inferred condition/reason relationships, and erroneous discharge reason. Dropping treatments.frequency/duration, surgeries.outcome/reason, diagnosis.condition/severity/time, discharge.follow up/referral, symptom intensity/temporalisation/behavior, and broad details elsewhere is a real information loss, not medical equivalence. Discharge summaries and retained details can contain some of this context naturally, but do not relocate removed fields into them automatically.

Preliminary projection measurements on the saved data: training target characters 3,105,034?2,045,281, **34.13% shorter**; scalar leaves 48,177?31,134, **35.38% fewer**. Validation characters 71,300?46,166, **35.25% shorter**; scalar leaves 1,082?693, **35.95% fewer**. These are characters/leaf counts, not tokenizer counts, training-time forecasts, or full 24K statistics. Inputs remain unchanged.

Projection removes 169 of 12,202 training list items and 2 of 268 validation list items because no selected child survives. Some surviving entries lack identifiers: training surgeries 29, treatments 13, tests 2 and symptoms 1; validation surgeries 1 and treatments 1. Projection also makes patient medical history newly empty in 54 training rows and discharge newly empty in 166 training rows (four validation rows for discharge). No projected exact-array duplicates were found in either split. Do not invent missing names or discard surviving unnamed entries silently. Review whether to reject/correct such rows before freezing v3.

Diagnostic-only rescoring of projected existing predictions gives mean strict F1 approximately 23.17% and soft F1 approximately 35.57%, versus 18.93%/30.74% originally. No predictions were regenerated and the two invalid outputs remain invalid. The scoring task is easier because fields were removed; this is **not a new fine-tuning result**, a clinical-quality improvement, or a fair cross-schema comparison.

## 8. Projection rules and quality limits for v3

Use the mapping above as an explicit allowlist. Preserve all parent keys and their types. Keep surviving values verbatim, omit absent inner fields, use empty objects/arrays, and retain the absent-visit-motivation convention. Drop an array item only if projection leaves it empty. Do not truncate arrays to enforce the 30-path schema budget.

The analysis projection does not relocate, summarize, repair clinical claims, invent values, or automatically deduplicate entries that become identical only after projection. Distinct original events can become indistinguishable when a distinguishing field is removed. Current v2 exact deduplication happens before this new projection; inspect and explicitly decide how projected collisions should be handled for v3, then freeze that rule. Do not silently change it while comparing data sizes.

Projection cannot correct false retained values, reversed negation, mixed chronology, or an erroneous reference relation. Define source-grounding rules and inspect a diverse sample of the projected references, particularly treatments, negation-bearing symptoms, unknown placeholders, unnamed entries, and admission/discharge distinctions. Retain explicit negatives in selected values when documented; never transform a negated symptom into a positive one. Do not use empty sections as evidence that no symptom/test/treatment existed beyond the supplied text.

The child-key cap also removes structured status/evidence fields: no new assertion/evidence keys are authorized by this mapping. Reviewers can record support quotes separately in audit artifacts without expanding the output schema. The remaining field names alone do not solve negation or chronology.

## 9. Next phase: 5,000 accepted examples under a new contract

1. **Implement separate v3 preparation and notebooks.** Reuse audited helpers where appropriate, but do not change v2 defaults/artifacts to point at new data. Use a new schema version, pointer, data version, prompt hash, comparison contract and result root. Proposed new names are implementation choices, not existing files.
2. **Inspect the full 24,000-row training candidate pool at the pinned revision**, apply documented conservative cleaning, project to the 30-path schema, inspect quality, and select exactly 5,000 eligible unique examples using a deterministic seed. Target is 5,000 accepted examples after filtering, not 5,000 candidates. Report actual rejection/deduplication counts. Use shuffled/representative sampling rather than just the next larger prefix. Broader source review may change the observed retention rate.
3. **Establish separation before sampling.** Check normalized-note overlap across training, validation and official test candidates and group near duplicates/related cases as feasible. Exclude overlap from training. Document the limits of duplicate detection. Previously inspected 30 cases are development cases, not an untouched test set.
4. **Freeze new reviewed evaluation subsets.** Suggested scale is 100 development examples from unused validation records and 100?200 final test examples from unused official test records, after leakage checks. These sizes are recommendations, not already prepared data. Review references against the actual supplied text. Keep test targets out of prompt/schema/hyperparameter decisions.
5. **Replace inherited SOAP wording**, list exactly the retained schema, and encode identical stored prompts for baseline and adapter. Use full assistant targets with strict masking and no silent truncation. Recompute token distributions, target lengths and context limits for the new data; do not infer token savings directly from character reduction.
6. **Run a fresh base-model baseline before training**, using the new schema/cases/contract. Preserve a common decoding protocol, normally generated-only 1.08 plus optionally pure greedy for diagnosis. Do not tune decoding on the final test set. Report raw and fence-stripped validity separately.
7. **Run label and model checks, then the 5,000-example LoRA experiment.** FP32/T4 and the established recipe are a reasonable starting point. Recheck longest-row forward/backward memory before disabling checkpointing. With batch 1/accumulation 8 and three epochs, 5,000 examples imply about 1,875 optimizer steps; this is a planning calculation, not a completed run. Use finite-loss checks, periodic checkpoints, development loss/quality monitoring and archived outputs. A lower loss alone does not establish better extraction.
8. **Evaluate actual usefulness.** Report allowed-key/type validity, raw/fence-stripped JSON validity, whole-object parse failures, field-aware strict/soft F1, omissions, unsupported assertions, negation, chronology and entity/event-linkage errors. Review a fixed sample against notes; invalid outputs may contain useful text but must remain invalid in headline strict scores. Never repair them into passing outputs without separately labeling that analysis.
9. **Separate schema and dataset-size claims.** New schema+prompt+data size together produce a combined-pipeline comparison. If claiming that increasing from 1,325 to 5,000 caused the gain, add a new-schema 1,325-example comparator trained from the same base on a subset of the 5,000 with the same evaluation contract. Record steps/tokens/epochs and compute, because equal epochs imply more optimizer updates for the larger dataset. Old full-schema F1 is not directly comparable with reduced-schema F1.
10. **Scale further only with evidence.** More clean diverse examples may help; larger volume with the same noisy annotations can reinforce errors. This experiment should answer whether the revised pipeline improves extraction enough to justify expanding toward the eligible full set.

## 10. Runtime, authorization and practical checks

User prefers Jupyter notebooks and has used VS Code with Colab. Local Explorer/workspace files and the remote kernel filesystem are separate; executed paths refer to the kernel machine. Upload required code/data to the runtime and download artifacts before stopping it.

Colab MCP was tested successfully during this exploration: OAuth status, CPU runtime creation, remote execution, synthetic upload/download round trip, and importing/scoring a repository module after upload. The user explicitly approved uploading this repository's data after an initial automatic approval rejection. That source upload then succeeded. The temporary smoke runtime was stopped; do not assume a current live session. GPU provisioning/training through MCP was not tested in this phase.

Hugging Face access is separate from Colab OAuth; Gemma needs accepted license/read access. Use cached authentication, environment variables or a hidden prompt; never print tokens or include credentials in documents/notebooks. Do not dump .env.local. No paid judge is required by the current workflow.

Local `.venv/Scripts/python.exe` works and reports Python 3.14.3. Plain `python` resolves to a broken Windows app alias in this environment. A separate Python 3.12/3.13 environment is recommended for the dedicated clinical dependency stack. Eight existing stdlib unit tests passed outside the sandbox after a temporary-directory permission failure inside it. No source implementation changed during the audit/handoff work, and no new GPU run was launched. Prefer scoped projection/self-checks when implementing v3 rather than rerunning training just to validate documentation.

There are unrelated user workspace changes, including .gitignore/IDE files and untracked HTML/sample files. Preserve them. Do not revert or commit unrelated changes. Existing audit documents were created in this conversation and should accompany this handoff.

## 11. Starting instruction for the fresh agent

Read this handoff, the source-grounding audit and the schema-analysis JSON. Implement a separately versioned clinical extraction pipeline targeting 5,000 accepted training examples and the exact 30-path schema above, retaining every parent. Preserve v2. Inspect projected-label quality, define/freeze new splits and prompts, run a base-model baseline, and verify labels and runtime memory before training. Keep per-run artifacts and report grounded extraction quality alongside JSON formatting. Do not resume the old pilot 1 versus pilot 2 investigation, silently restore the full child schema, or adopt the rejected 15-scenario 100k dataset.
