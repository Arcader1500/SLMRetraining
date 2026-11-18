# Paired DeepEval setup

**Rubric update:** the source-note reevaluation uses the same 20 saved pairs and
two fidelity/coverage dimensions, with a separately versioned contract. See
[SOURCE_GROUNDED_REEVALUATION.md](SOURCE_GROUNDED_REEVALUATION.md). The original
reference-only protocol and results below remain preserved for comparison.

**Codex evaluation completed with `gpt-6-luna` on all 20 selected cases.**
The user requested this model instead of the originally prepared `gpt-6.1-sol`.
All 40 output/reference comparisons and 80 metric measurements completed; all
six notebook code cells have executed outputs. **Gemini remains disabled and was
not called.** The original extraction experiment and outputs are unchanged.

| Mean judge score (0?1) | Baseline | Fine-tuned | Paired difference |
| --- | ---: | ---: | ---: |
| Reference fidelity | 0.335 | 0.375 | +0.040 |
| Reference coverage | 0.410 | 0.455 | +0.045 |

These are modest reference-agreement gains, not a clinical accuracy assessment.
Fine-tuned fidelity was higher on 10 cases, equal on six and lower on four;
coverage was higher on 11, equal on seven and lower on two. No significance or
judge-calibration claim is made.

Results: `results_v3/deepeval_20/judgments/a6bb10a9fde5e2b4/` contains all scores,
reasons, original format flags, paired CSV, summary, run contract and completion
checks. `results_v3/deepeval_20/execution_provenance.json` records CLI version and
source hashes. The frozen selection manifest's `judge_status=not_run` records
its original preparation state; use the run summary or `notebook_execution.json`
for current execution status.

## Frozen comparisons

The pipeline selects 20 unique cases from all 100 phase-2 development cases using
`random.Random(42).sample(sorted(case_ids), 20)`. Each selected note contributes:

| DeepEval field | Baseline comparison | Fine-tuned comparison |
| --- | --- | --- |
| `input` | Original clinical note | Same clinical note |
| `expected_output` | Dataset reference JSON | Same dataset reference JSON |
| `actual_output` | Saved baseline output | Saved fine-tuned output |

The model names are not included in judge prompts. Both models use exactly the
same IDs and references. There are 40 output/reference comparisons, with two
G-Eval metrics each: **80 metric measurements**. Actual provider requests may be
higher. No additional model generation or training is required.

Sampling does not filter on validity or score: all 20 selected baseline outputs
and three selected fine-tuned outputs fail raw JSON validity. Outputs are saved
verbatim. The frozen files are:

- [selection_manifest.json](../../results_v3/deepeval_20/selection_manifest.json): IDs,
  seed, source hashes, comparison-contract digest and metric instructions.
- [paired_cases.json](../../results_v3/deepeval_20/paired_cases.json): original notes,
  references, both outputs and saved deterministic format/fact metrics.
- [judge_settings.json](../../results_v3/deepeval_20/judge_settings.json): execution
  switches, enabled providers and explicit judge model names.
- [04_deepeval_paired_20.ipynb](../../notebooks/v3_1325/04_deepeval_paired_20.ipynb):
  preparation and later opt-in execution.

Preparation validates the saved references/prompts against the frozen dataset,
case IDs and hashes. Re-preparation refuses a changed sample or source artifact;
use a new output directory for a different experiment.

## Judge options

| Option | Prepared model | Current setting |
| --- | --- | --- |
| Codex CLI | `gpt-6-luna` | Default backend; completed |
| Google AI Studio API | `gemini-3.8-flash` | Disabled; blocked until Codex finishes |

Codex is a custom `DeepEvalBaseLLM` adapter around `codex exec`, with a fresh
ephemeral, read-only session for each judgment and schema-constrained JSON output.
It ignores user config/project instructions for judging, while reusing CLI
authentication. On Windows it invokes the native executable to preserve UTF-8.
Check `codex login status`: ChatGPT login uses subscription-based Codex access;
API-key login uses API billing. Account/model access and usage limits still apply.
This is a custom bridge, not a built-in DeepEval subscription integration.
OpenAI recommends API-key authentication for programmatic CI/CD workflows.
See [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode)
and [authentication](https://learn.chatgpt.com/docs/auth?surface=cli).

The CLI adapter does not return token log probabilities, so native G-Eval's
probability-weighted score normalization is unavailable. Do not merge Codex and
Gemini scores into one metric series; each judge gets a separate run contract.
See [DeepEval custom judges](https://deepeval.com/guides/guides-using-custom-llms)
and [G-Eval](https://deepeval.com/docs/metrics-llm-evals).

For the later Gemini comparison, **3.8 Flash** is the suggested default because
this is a small judgment set where reasoning quality matters more than throughput.
That is a task-specific recommendation, not a clinical benchmark result.
Google describes [3.8 Flash](https://aistudio.google.com/docs/models/gemini-3.8-flash)
as its most intelligent Flash model and
[3.5 Flash-Lite](https://aistudio.google.com/docs/models/gemini-3.5-flash-lite) as
optimized for efficiency and simple data processing. Both have free-tier token
pricing listed in [Google's pricing page](https://aistudio.google.com/docs/pricing);
availability and rate limits depend on the project. Adding a key never enables
Gemini automatically. There is no provider fallback on failure.

## Running later

Use a separate Python 3.12/3.13 environment:

```powershell
py -3.13 -m venv .venv-deepeval
.venv-deepeval/Scripts/python.exe -m pip install -r requirements-deepeval.txt
```

The current workspace already has an isolated, tested environment at
`.venv/deepeval-tools/`. It does not change the training environment.

To prepare or validate the frozen sample without any judge calls:

```powershell
.venv/Scripts/python.exe -m scripts.prepare_deepeval
.venv/Scripts/python.exe -m scripts.run_deepeval
```

To run Codex later, choose a model your account can access, set `run_judge=true`
in the settings, and run the explicit execution command:

```powershell
.venv/deepeval-tools/Scripts/python.exe -m scripts.run_deepeval --run --backend codex
```

In the notebook, `RUN_JUDGE=True` is the equivalent additional switch. A model
name is frozen in the run contract; changing it starts a separate results folder.
The initial pipeline preparation made no judge calls; the subsequent user-authorized Codex run is now complete.

Only after the Codex run completes, enable Gemini explicitly in settings, set
`GOOGLE_API_KEY` in the process/kernel environment, install the declared Gemini
SDK dependency, and choose the Gemini backend. Never paste a real key into a
notebook, command history, saved settings or results. A missing key produces an
error; it does not fall back to Codex or another provider.

## Scores, checkpoints and limits

Two G-Eval metrics use fixed instructions:

- **Reference fidelity:** precision of expressed claims relative to the reference,
  including contradictions, negation, doses, chronology and event assignment.
- **Reference coverage:** omissions or distorted reference facts, allowing
  equivalent wording and ignoring empty/placeholder fields.

The metrics receive only actual and expected output. Notes are retained for
human review, not silently used as an alternative grading source. These scores
measure agreement with synthetic annotations, not clinical correctness. Additional
facts absent from the reference are unsupported *relative to the reference*,
which does not prove they are absent from the note.

The judge may credit readable facts in malformed JSON. It never repairs the
saved output. This semantic scoring differs from the deterministic fact evaluator,
which zeros malformed whole objects. Raw/fence-stripped validity, schema flags
and the existing strict/soft F1 remain separate.

Every metric result is checkpointed, with reasons and original format flags, in
`results_v3/deepeval_20/judgments/<contract-hash>/scores.json`. Completed items are
skipped on resume. Errors stop the run rather than being scored as zero. A complete
run writes `paired_comparison.csv` and `summary.json`, including paired deltas.
Model order alternates between cases; judge sessions and metric instances are
independent. No Confident AI login/upload is required; telemetry is disabled.

Offline stubs were used for initial compatibility checks. The real Codex run is now complete; Gemini connectivity and judging remain untested and disabled. GPT-6 Luna scores have not been calibrated against clinician judgments.
