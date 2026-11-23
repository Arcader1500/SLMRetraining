# Full-schema v2, 5,000-example experiment

**Training, generation, and all 400 local Luna and 400 Gemini 4 Hydrogen judgments are complete.**
Training ran for three epochs and 1,875 steps, selecting checkpoint 1875 with
development loss 0.4552387595. Both sets of generations, the initial `gpt-6-luna`
evaluation (`c53d6fbd06d96102`), and the subsequent `gemini-4-hydrogen` evaluation
(`8993a8dd5f5f3a18`) are saved locally. The Colab runtime was released after generation.
See [results and verification](../../results_v2_5000/README.md). The protocol
and earlier progress notes below describe the experiment's recorded history.


Requested 19 November 2026. The user explicitly approved uploading the dataset/
prompt bundle and Hugging Face read token to Google Colab. Both uploads succeeded
to the `clinical-v2-5000` T4 runtime. Local temporary credential removed; the
remote temporary file is removed by the pipeline immediately after loading.
Preparation/execution is in progress; see `results_v2_5000/experiment_status.json`.
The earlier automatic-review upload rejection was resolved by this explicit
user authorization. Historical experiment artifacts remain unchanged.

## Frozen choices

| Setting | Value |
| --- | --- |
| Schema, cleaning, prompt | Original v2, including original system wording; no child-field projection, source-label repair or clinical quality filtering |
| Training examples | Exactly 5,000 accepted unique notes: preserve original 1,325 rows verbatim, add 3,675 |
| Additional selection | Seed-42 shuffle of upstream training indices >=1,500; consume until exactly 5,000 accepted |
| Existing v2 acceptance | Parse/schema checks, missing-placeholder cleanup, exact array deduplication, complete sequence <=4,096 tokens; no silent truncation |
| Leakage exclusion | Normalized exact notes checked against v2-eligible validation notes, frozen 100 notes and selected training notes |
| Development examples | Exact ordered 100 IDs and notes from `e80798edebe5aba5/validation.jsonl`; no resampling |
| Development targets/prompt | Reconstruct original full-schema v2 from pinned source; verify projection equals each frozen v3 target |
| Source | `AmareshHebbar/clinical-summarizer-sft`, revision `4ca20e0a38cc9235045c973b5503d49952fd1fac` |
| Base | `google/gemma-3-270m-it`, revision `ac82b4e820549b854eebf28ce6dedaf9fdfa17b3` |
| Runtime | T4, FP32; transformers 4.57.6, datasets 4.8.5, peft 0.18.1, accelerate 1.15.0 |
| Training | Three epochs, batch 1, accumulation 8: 1,875 optimizer steps |
| Optimizer/schedule | Learning rate 2e-4, cosine, warmup 0.08, weight decay 0.01, max gradient norm 1.0 |
| LoRA | Rank 16, alpha 32, dropout 0.05; all seven attention/MLP projections |
| Memory check | Actual longest-row FP32 forward/backward; enable gradient checkpointing only if preflight runs out of memory; record actual setting |
| Adapter selection | Lowest epoch-end development loss, matching the original v2 recipe |
| Generation | Greedy, generated-only repetition penalty 1.08, maximum 2,048 new tokens |
| Judge | DeepEval 4.3.4 with authenticated Codex CLI `gpt-6-luna`; Gemini disabled |
| Judge scope | Same `source_grounded_v2` rubric and two metrics as previous 100-case evaluation |
| New judgment count | 100 notes x 2 models x 2 metrics = **400**; no reused old scores, extra calibration or reference-only judge calls |

The ordered validation-ID digest is
`5632a34cfc1bc1b62172a975493cea1685613bdc9399e7cb22573d24425bedd5`.
The old v2 30-case development set has zero case-ID overlap with these 100.
V3 saved baseline generations use different prompts. Therefore both sets of
100 model outputs must be generated for this experiment.

## Execution artifacts

New notebooks: [notebooks/v2_5000](../../notebooks/v2_5000/).
They derive from preserved v2 notebooks; historical sources and outputs are
unchanged. `00_prepare_dataset` prepares the versioned data, `01_baseline_eval`
generates the base outputs, `02_finetune` trains from the original base, and
`03_eval_and_compare` generates fresh adapter outputs and scores both models.

The prepared pointer is `prepared_clinical_dataset/latest_v2_5000.json`.
All results go under `results_v2_5000/`, including comparison contracts,
per-case outputs/diagnostics, adapter, checkpoints, loss logs, pipeline state
and the 400-measurement judge run under `deepeval_100/`.

Preparation completed as dataset `3f8f10951130896b`: 5,000 training and 100
development rows, downloaded locally with both split hashes verified. Original
v2 row/tokenization equivalence, fixed validation source hashes and full-to-reduced
target correspondence passed. Adding 3,675 rows consumed 4,360 candidates; 685
were rejected by the existing acceptance/deduplication rules. Longest training
sequence is 1,651 tokens. Each epoch has 2,441,794 supervised tokens (7,325,382
across three epochs). Baseline generation is in progress.

After authorized code/data and credential transfer, extract the input archive
under `/content/clinical_v2_5000`, install the pinned notebook dependencies and run:

```bash
cd /content/clinical_v2_5000
python -u scripts/run_v2_5000_pipeline.py
```

The pipeline reads `/content/.clinical_v2_5000_hf_token` into its process
environment and removes that temporary remote file. No credential is printed
or included in notebook outputs. Each stage uses a separate notebook kernel;
real cell outputs/status are checkpointed by the existing nbclient runner.
Training retains optimizer checkpoints and resumes from the latest checkpoint.
Generation resumes completed per-case outputs. Download prepared data, outputs,
adapter/checkpoints and executed notebooks before releasing the runtime.

Once all generation artifacts are downloaded into this workspace, prepare/check
the frozen pairs without judge inference:

```powershell
.venv/deepeval-tools/Scripts/python.exe -m scripts.evaluate_v2_5000
```

Execute the authorized Luna run with:

```powershell
.venv/deepeval-tools/Scripts/python.exe -u -m scripts.evaluate_v2_5000 --run
```

Each successful metric score and reason is atomically checkpointed. Completed
keys are skipped on resume; changed inputs are rejected, and provider/usage
failures stop rather than becoming zero scores. There are 400 successful metric
judgments planned; an interrupted provider call before its checkpoint may need
repeating, as in the previous runner. DeepEval execution is local, using the
existing authenticated CLI, after remote generation artifacts are downloaded.

## Interpretation and checks

Same cases allow paired per-case comparison, but this run changes both schema
and training size relative to v3. It does not isolate either cause. Three epochs
also increase optimizer updates from 498 to 1,875; report supervised tokens and
runtime. Full-schema reference F1 and development loss are not directly
comparable with reduced-schema values. Keep the existing source rubric for
continuity: its coverage scope remains the earlier retained-field scope, while
references now provide a full-schema checklist. A future expanded full-schema
coverage rubric would need a separate comparison, rather than silently replacing
the old rubric. Synthetic label defects and incomplete source notes remain.
Near duplicates, patient grouping and official test separation are unestablished.

Offline tests check full-field retention/masking, deterministic extension with
overlap rejection, and 400 simulated judgments with no repeated saved keys.
They make no model calls. Windows sandbox temporary-directory permissions
required running the checks outside the sandbox.

```powershell
.venv/deepeval-tools/Scripts/python.exe -m unittest tests.test_v2_5000_experiment -v
```
