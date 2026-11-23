# Full-schema v2 / 5,000-example session handoff

## 23 November 2026 Gemini 4 Hydrogen evaluation complete

Local DeepEval saved all 400 `gemini-4-hydrogen` judgments (`backend: gemini`)
for the 100 frozen cases under the unchanged `source_grounded_v2` rubric. Run
`8993a8dd5f5f3a18` recorded:

- **Source fidelity:** `0.386 -> 0.539` (`+0.153`, 68W / 21T / 11L; 100k paired BCa 95% CI `[+0.115, +0.190]`)
- **Source coverage:** `0.412 -> 0.550` (`+0.138`, 69W / 17T / 14L; 100k paired BCa 95% CI `[+0.101, +0.175]`)

- [Summary](../../results_v2_5000/deepeval_100/judgments/8993a8dd5f5f3a18/summary.json)
- [Paired comparison](../../results_v2_5000/deepeval_100/judgments/8993a8dd5f5f3a18/paired_comparison.csv)
- [Scores and reasons](../../results_v2_5000/deepeval_100/judgments/8993a8dd5f5f3a18/scores.json)

[SLM_Clinical_Extraction_Overview.html](../SLM_Clinical_Extraction_Overview.html)
was updated to report these Gemini 4 Hydrogen results for `Full · 5,000` and
add a tabbed 100-case Paired Bootstrap 95% CI view.

## 20 November 2026 Luna evaluation complete

Local DeepEval 4.3.4 saved all 400 `gpt-6-luna` judgments for the 100 frozen
cases under the unchanged `source_grounded_v2` rubric. Run `c53d6fbd06d96102`
finished at 07:15 UTC. Verification confirmed the frozen inputs, all 400 unique
score keys, and the 200 paired CSV rows. The evaluator has exited.

- [Summary](../../results_v2_5000/deepeval_100/judgments/c53d6fbd06d96102/summary.json)
- [Completion checks](../../results_v2_5000/deepeval_100/judgments/c53d6fbd06d96102/completion_checks.json)

## 20 November 2026 adapter generation complete

Checkpoint 1875 generated all 100 outputs using dataset `3f8f10951130896b`
and the original full-schema baseline contract. Colab session
`clinical-v2-5000-generation` used a Tesla T4. Checks and local exports ran
at intervals under ten minutes. The final export was verified locally and
the runtime was released.

- [Results index](../../results_v2_5000/README.md)
- [Comparison summary](../../results_v2_5000/comparison/summary_comparison.csv)
- [Local verification](../../results_v2_5000/generation_completion_checks.json)
- [Executed notebook](../../notebooks/v2_5000/03_eval_and_compare.ipynb)

The training, recovery, and launch instructions below describe earlier stages.

## Completed and stopped ? authoritative final state

Training completed and artifacts were downloaded/verified on 2026-11-19T13:05:06.796811+00:00.
**Three epochs, global step 1875, selected checkpoint 1875, best development loss
0.4552387595.** Adapter/tokenizer, optimizer checkpoints 625/1250/1875, metrics,
logs and executed notebook are local. All 39 exported file hashes verified; all
252 adapter tensors finite and exactly equal to selected checkpoint weights.
The recovery runtime `clinical-v2-5000-recovery` was explicitly released after
verification. No monitor/timer remains pending. **Stop work here**, per latest
user instruction. No fresh adapter generations and no Luna calls were launched.

Read `results_v2_5000/README.md`, `training_completion_checks.json` and
`experiment_status.json` for the final state. All running/PID/session/timer
instructions below are historical. Do not restart the pipeline automatically.
The original session's unexplained disappearance remains recorded separately
from the deliberate shutdown of the successful recovery runtime.


## Latest user scope: stop after training artifacts are saved

The user instructed: keep monitoring and stop after training is complete and
adapters/results are saved. Treat this as a stop after training and local artifact
verification, **before** fresh adapter generation and Luna evaluation. At this
request the recovery training child remained active. The pipeline parent PID
1498 was deliberately SIGSTOPped (state T) while blocked waiting for its training
child PID 1503; this prevents automatic advancement to notebook 03 while allowing
training to continue. **Do not SIGCONT or restart the parent.** The stopped parent
is intentional, not a hung training job. Remote `results_v2_5000/stop_after_training.json`
records this hold. Continue checking the training child and notebook-02 status
on ten-minute timers. When training completes, download and verify metrics,
selected adapter, checkpoints and executed notebook; then release the runtime
and stop work. Do not start notebook 03 or a judge run under this latest scope.


## Recovery active ? current state supersedes earlier incident/snapshots

Recovery started 2026-11-19T11:13:25.504885+00:00. Current Colab session is
**`clinical-v2-5000-recovery`**, endpoint **`gpu-t4-s-usw1b0-30d9xhsa4bbas`**,
Tesla T4. Remote root remains `/content/clinical_v2_5000` so saved checkpoint
paths remain valid. Pipeline PID **1498** at launch. No old runtime assignments
were present. A verified recovery archive restored the same 5,000/100 data,
all 100 completed baseline outputs, and the step-625 model/optimizer/scheduler/
RNG checkpoint. Preparation and baseline stages are marked complete and skipped.
Recovery archive: local `.venv/v2_5000_transfer/recovery_input.zip` (93,001,913
bytes), remote `/content/clinical_v2_5000_recovery.zip`, SHA-256
`555e2d2a2ff4f881cf3ba39b84b0be6648cf845fbeb24b0fe21984b261e5cbad`.
Large upload failed with a connection error; six chunk uploads succeeded and
reassembly hash was verified. No dataset/target/generation contract was changed.

**User now explicitly requires a runtime ping every 10 minutes, including during
long waits.** Do not sleep for one or two hours without those pings. On every
ping, inspect remote pipeline/process state and live logs, and download any
newly complete optimizer checkpoint plus progress metadata. Record each ping and
next planned UTC time in `results_v2_5000/experiment_status.json`. If the agent
turn ends, another agent must take over; this is not a durable timer service.

Recovery resume is verified: fresh logs advanced from step 740 to 860 during
the first two ten-minute pings. Current step is in the machine-readable status. The restored `training_log.json`
may temporarily still show old step 860 until the first resumed log overwrites
it; do not mistake that stale log for fresh recovery progress. The exact same
three-epoch schedule ends at global step 1875. Judge execution remains local,
400 Luna measurements, after fresh adapter outputs are downloaded.


## Current incident: runtime absent ? supersedes running-state snapshots below

Checked 2026-11-19T11:02:53.412073+00:00. Colab MCP `list_sessions` returned no server runtime
assignments. `session_status("clinical-v2-5000")` returned session not found.
The original endpoint is no longer available through Colab. No stop command was
issued by this agent for that active endpoint. The cause of removal is **unknown**;
no provider termination reason or final remote traceback is available. Do not
state that an idle timeout, preemption, OOM or training exception is established.

Last verified remote progress: training step 860, epoch 1.376, finite loss 0.4718
at 08:28 UTC. An ensuing two-hour wait had no automatic artifact exports. Training
may have advanced farther, but those results are unverified and unavailable.
Locally safe: prepared 5,000/100 dataset, all 100 baseline outputs and scores,
and step-625 model/optimizer/scheduler/RNG checkpoint. Fresh adapter generations
and Luna judgments have not been verified; no judge calls were launched.

The runtime must **not** be treated as still running. Recovery has not started.
A replacement runtime can restore local artifacts and resume from step 625;
never regenerate the prepared data or completed baseline unnecessarily. Existing
upload authorization still applies. Reassess monitoring and automatic external
checkpoint backup before another long unattended wait. The older paths/PIDs and
running-state descriptions below are historical snapshots, not live state.


Updated **2026-11-19 08:23 UTC (13:53 IST)**. This is the active task; the earlier
training-label audit is separate. Read the live state before acting: counts and
PIDs below are a snapshot, not instructions to start a second writer.

## User request and authorization

Run original **full-schema v2 as-is**, with 5,000 accepted training examples,
three epochs, the **same ordered 100 validation notes** as v3, base generations,
fresh adapter generations, then **400 local GPT-6 Luna / DeepEval judgments**
(100 x two models x fidelity/coverage). Do not prune child fields, repair labels,
change rank/model, resample development cases, add a judge calibration batch or
rerun the old v3 judgments. Keep the existing `source_grounded_v2` rubric.

The user explicitly approved uploading the dataset/prompt bundle and Hugging
Face read token to Google Colab. Both transfers succeeded. **This authorization
persists; do not ask again for the same experiment transfers.** Initial automatic
review rejections preceded and were resolved by this explicit approval.

**Colab does not run Codex or Luna.** It handles preparation, base generation,
training and adapter generation. Download outputs, then run DeepEval **locally**
through the existing authenticated Codex CLI. Codex authentication was checked:
`Logged in using ChatGPT`. No Codex credentials were transferred to Colab.
The temporary Hugging Face token files were removed locally and remotely; the
live pipeline passes the read token through its process environment to children.
Never print credentials or process environments.

## Monitoring preference

The user requested timers instead of continual polling. The active agent is
waiting about two hours before the next inspection, expecting training and
adapter generation to complete. The full baseline and first-epoch optimizer/model
checkpoint (step 625) are already backed up locally. The planned next-check UTC time is recorded in
`results_v2_5000/experiment_status.json`. This is an interruptible wait in the
active agent turn, **not a durable scheduled task**. Another agent should inspect
live state on takeover; no automatic local judge launcher has been installed.

## Live session and exact locations

| Item | Value |
| --- | --- |
| Colab MCP session name | **`clinical-v2-5000`** |
| Runtime endpoint | `gpu-t4-s-ass1b0-35cr2rlo55mbh` |
| GPU | Tesla T4, 15,360 MiB; FP32 |
| Runtime URL | `https://8080-gpu-t4-s-ass1b0-35cr2rlo55mbh-b.asia-southeast1.prod.r.colab.dev` |
| Remote project / working directory | **`/content/clinical_v2_5000`** |
| Remote results | `/content/clinical_v2_5000/results_v2_5000` |
| Remote notebooks | `/content/clinical_v2_5000/notebooks/v2_5000` |
| Pipeline process PID at snapshot | **1939** |
| Training notebook runner PID at snapshot | **15363** |
| Pipeline launcher log | `/content/clinical_v2_5000_pipeline.log` |
| Stage/status file | `/content/clinical_v2_5000/results_v2_5000/pipeline_status.json` |
| Local project | `C:/Users/atharva.bedekar/PycharmProjects/SLMRetraining` |
| Local results | `results_v2_5000/` under the project |
| Local status summary | `results_v2_5000/experiment_status.json` |

Use `mcp__colab_mcp__list_sessions`, `session_status`, `exec_code`, `download_file`
and `upload_file` through tool discovery (`ALL_TOOLS`). **Reconnect to the existing
session rather than creating a new runtime.** Do not stop the runtime before
downloading and verifying its outputs/checkpoints. Session names survive agent
turns; the Python variable named `pipeline` in the control kernel is convenient
but not required. Use the process table and disk state if that variable is absent.

## Completed and pending work

- Preparation complete: **dataset `3f8f10951130896b`, 5,000 train / 100 validation**.
- Prepared dataset, Arrow dataset, manifest and executed preparation notebook are
  downloaded locally. Both split hashes verified. Local checks are saved in
  `results_v2_5000/preparation_local_checks.json`.
- Original 1,325 v2 training rows preserved verbatim; 3,675 added from seed-42
  shuffled indices >=1,500 under original v2 acceptance/deduplication rules.
  685 additional candidates rejected; no new clinical quality filter.
- Frozen 100 IDs, order, source hashes and notes preserved. Full v2 references
  reconstructed from pinned source; their v3 projections match frozen targets.
- All 5,100 label masks checked; 5,000 unique normalized training notes and no
  normalized exact-note overlap with the 100 development notes.
- Longest training sequence 1,651 tokens. 2,441,794 supervised tokens per epoch;
  7,325,382 across three epochs. Three epochs imply **1,875 optimizer steps**.
- **Baseline complete: 100/100 outputs downloaded and locally verified** against
  contract IDs, diagnostics and per-case CSV. Executed baseline notebook saved.
- **Training running:** step 850/1,875 (epoch 1.36) at the latest observation. Longest-row
  forward/backward finite; peak allocation 8.323 GiB. No gradient checkpointing
  was needed. The step-625 model/optimizer/scheduler checkpoint has been downloaded and verified locally.
- Adapter generations and local Luna evaluation have not started; zero new judge
  calls. Training notebook runner PID is 15363; pipeline PID remains 1939.
- The remote pipeline automatically advances baseline -> training -> comparison.
  It does **not** automatically download outputs or launch local Luna evaluation;
  an agent must do those steps.

## Inspect progress without changing anything

Run through `exec_code(session="clinical-v2-5000", ...)`:

```python
from pathlib import Path
import json, subprocess
root = Path('/content/clinical_v2_5000')
result = root / 'results_v2_5000'
print((result / 'pipeline_status.json').read_text())
print(subprocess.run(['pgrep', '-af',
      'run_v2_5000_pipeline|run_colab_notebook'],
      capture_output=True, text=True).stdout)
for label, path in [
    ('base', result / 'baseline/gen_rp_1.08/generations.json'),
    ('adapter', result / 'comparison/finetuned__gen_rp_1.08/generations.json')]:
    if path.exists():
        print(label, len(json.loads(path.read_text())))
log = result / 'finetuned_v2_5000/training_log.json'
if log.exists():
    entries = json.loads(log.read_text())
    print(entries[-1] if entries else 'training starting')
```

Stage logs are `results_v2_5000/<notebook-stem>.log`; notebook cell execution
state is `notebooks/v2_5000/<stem>.status.json`. Executed outputs are saved to
`<stem>_output.ipynb`. During a long cell, notebook outputs may lag current
per-case JSON or live training logs. A transient JSON read error can occur if
reading generation files during a write; reread after the write completes.

## What is resumable, and limits

- **Generation:** each successful case is saved to `generations.json` with
  `generation_diagnostics.json`; rerun skips cases present in both. An interrupted
  case may be regenerated. This applies separately to base and adapter.
- **Training:** Hugging Face `get_last_checkpoint` and
  `trainer.train(resume_from_checkpoint=...)` restore saved model/optimizer/RNG
  state. Checkpoints are saved **at epoch boundaries** (steps 625, 1250, 1875),
  not every logged step. Work after the last checkpoint can repeat. Before the
  first checkpoint, interruption requires restarting training. The live loss log
  is progress evidence, not a restorable optimizer checkpoint.
- **Stages:** `pipeline_status.json` records the completed stages and skips them
  on restart. A crash after a stage completes but before the parent records it
  needs inspection of that notebook's status and artifacts before marking it done.
- **Judging:** the existing runner atomically checkpoints each metric score/reason
  and skips completed `(case_id, model, metric)` keys. Only an interrupted call
  before its checkpoint may need repeating. Exactly 400 successful measurements
  are planned. Provider/quota failures stop and preserve progress.
- **Persistence:** resuming on the same VM retains files. A released/lost Colab
  VM does not: download artifacts/checkpoints periodically. The local prepared
  dataset and currently downloaded baseline outputs survive agent limits.
- **Single writer:** the notebook pipeline has **no writer lock**. Never launch a
  second pipeline while its parent **or child notebook kernel** is still alive.
  Judge execution has an OS writer lock; still avoid duplicate launch attempts.

If the pipeline truly exited, first inspect failure/status/logs. If auth is
needed, restore the approved HF token to the exact temporary remote file
`/content/.clinical_v2_5000_hf_token` through the upload tool; obtain it locally
without printing it. No Codex token goes to Colab. Remove the local temporary
file after successful upload. Then, only after confirming no old writers remain:

```python
import subprocess, sys
log = open('/content/clinical_v2_5000_pipeline.log', 'a')
process = subprocess.Popen(
    [sys.executable, '-u', 'scripts/run_v2_5000_pipeline.py'],
    cwd='/content/clinical_v2_5000', stdout=log,
    stderr=subprocess.STDOUT, start_new_session=True)
print('Restarted pipeline PID', process.pid)
```

If a finished `adapter/adapter_config.json` already exists but stage completion
was not recorded, the training notebook deliberately refuses to overwrite it.
Verify its complete three-epoch metrics, contract and notebook state, then repair
the stage bookkeeping rather than deleting the adapter or blindly retraining.

## Download and finish

Download prepared data, baseline, `finetuned_v2_5000/` (including checkpoints),
comparison, logs/status and all executed notebooks using remote ZIP files plus
`download_file`. Create archives with paths relative to the remote project so
extraction into the local project preserves layout. Do not include the HF cache,
credential files or process environments. Transfer ZIPs can live in local
`.venv/v2_5000_transfer/` (ignored by Git). Preserve original v1/v2/v3 artifacts.

Current transfer files:

- Local `.venv/v2_5000_transfer/input.zip`: uploaded code/notebooks and frozen
  inputs; **no credential**. Also remote `/content/clinical_v2_5000_input.zip`.
- Local `.venv/v2_5000_transfer/training_checkpoint.zip`: first-epoch model,
  optimizer, scheduler and RNG state, plus live logs/status; remote
  `/content/v2_5000_training_checkpoint.zip`.
- Local `.venv/v2_5000_transfer/prepared.zip`: completed preparation archive;
  remote `/content/v2_5000_prepared.zip`.
- Local `.venv/v2_5000_transfer/baseline_progress.zip`: complete 100-case baseline and initial training metadata;
  remote `/content/v2_5000_baseline_progress.zip`.

Validate complete 100-case generations/diagnostics and frozen contracts before
starting the judge. Copy completed `_output.ipynb` snapshots onto the corresponding
new canonical notebooks after checking actual execution counts and no errors;
keep snapshots too. The preparation notebook already has its executed outputs.

**Locally**, from the project root:

```powershell
# Prepare/freeze the pairs only; no model calls.
.venv/deepeval-tools/Scripts/python.exe -m scripts.evaluate_v2_5000

# Execute or resume the same 400 Luna measurements.
.venv/deepeval-tools/Scripts/python.exe -u -m scripts.evaluate_v2_5000 --run
```

Judge files will be `results_v2_5000/deepeval_100/judgments/<contract-hash>/`,
including `scores.json`, `progress.json`, `summary.json` and
`paired_comparison.csv`. Root `deepeval_100/progress.json` mirrors progress;
the explicit resume command is recorded in `deepeval_100/execution.json`.
Do **not** run `scripts.run_deepeval --remaining-validation`: that is the old
v3 evaluation, not this experiment. Do not replace `gpt-6-luna` with another model.

Windows sandboxing has caused temporary-directory/CLI permission failures. The
three offline tests passed outside the sandbox. Use a scoped, approved execution
outside the sandbox if the actual judge has the same issue; do not change scores
or treat failures as zero. Local Codex auth is available and does not require
credential forwarding to Colab.

## Files, checks and interpretation

Implementation: `scripts/prepare_v2_5000_dataset.py`,
`build_v2_5000_notebooks.py`, `run_v2_5000_pipeline.py`, `evaluate_v2_5000.py`;
new notebooks under `notebooks/v2_5000/`. The uploaded preparation source is
snapshotted under `results_v2_5000/execution_sources/`, with upload hashes.

One local parser fix after uploading: new JSONL readers use `.split('\n')`
with empty-line exclusion because four Unicode separators inside valid note
strings caused `.splitlines()` to split records. Local split hashes now verify.
The original remote preparation **already completed successfully**. Its old cache
reload branch still uses `.splitlines()`; if rerunning preparation rather than
skipping its completed stage, upload the current local preparation script first.
Do not rebuild the data or alter frozen hashes to hide that source difference.

`tests/test_v2_5000_experiment.py`: three offline tests passed, including full-field
retention/masking, duplicate/overlap rejection, and 400 simulated measurements
with no repeated completed keys. Notebook Python cells compile. No code-review
agent/workflow was invoked, matching the user's established preference.

The full [protocol](FULL_SCHEMA_V2_5000_RUN.md) records exact model/dataset revisions
and hyperparameters. Same cases permit paired output comparisons, but this run
changes schema **and** training size relative to v3. Keep reference F1 and loss
cross-version limitations explicit; the unchanged source rubric preserves its
earlier coverage scope. User requested the experiment even if results decline.

Do not revert concurrent work: prior audit/statistics/docs changes were already
uncommitted, and `results_v3/training_audit_100/progress.json` changed during this
session from another writer. No commit, push or merge has been requested.
