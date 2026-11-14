# Clinical Gemma fine-tuning workflow

1. Run [prepare_clinical_dataset.ipynb](./prepare_clinical_dataset.ipynb).
   - Defaults to 1,500 candidate training rows and 10 validation cases.
   - Conservatively repairs JSON control characters, rejects unresolved syntax/schema problems, and removes exact normalized-note duplicates.
   - Saves the cleaned DatasetDict, JSONL exports, complete token sequences, assistant-only labels, preparation logs, and manifest under `prepared_clinical_dataset/<version>/`.
   - Uses a 4,096-token complete-sequence limit; overlength rows are excluded, never silently truncated.
   - Download and preserve `prepared_clinical_dataset.zip` from the remote runtime.
2. Run [prepared_baseline_evaluation.ipynb](./prepared_baseline_evaluation.ipynb).
   - Uses the prepared validation split and stored prompt text, with the original Gemma weights.
   - Defaults to FP32, greedy generation, and 2,048 output tokens. No paid judge is used.
   - Saves raw outputs, token diagnostics, comparison contract, and per-case/aggregate metrics under `baseline_prepared_evaluation/`.
   - The frozen validation selection, prompt, tokenizer, generation settings, and metric definitions must also be used for the fine-tuned evaluation.
3. Run [train_prepared_clinical.ipynb](./train_prepared_clinical.ipynb) with `RUN_TRAINING = False` first.
   - Set `BASELINE_DIR` to the completed numbered baseline folder on the remote runtime.
   - Verifies the exact prepared version, baseline prompts/selection, and all saved assistant-only labels.
   - Checks finite loss and backward gradients on the longest training row without optimizer updates.
   - After reviewing the checks, enable `RUN_TRAINING` for the 60-step LoRA pilot. It saves the adapter, training logs, and copied baseline contract.
4. Run [compare_pilot_clinical.ipynb](./compare_pilot_clinical.ipynb).
   - Upload the prepared dataset, completed numbered baseline folder, and `pilot_01/` with its adapter to the same runtime.
   - Runs inference on the same 10 validation cases using the saved baseline contract and original metric definitions.
   - Reuses saved baseline outputs; saves adapter outputs, aggregate changes, and per-case comparisons under `pilot_01_comparison/`.

The existing [main.ipynb](./main.ipynb) still contains the original 512-token training recipe and is **not yet connected to the prepared dataset**. Do not use it unchanged for the pilot.

[baseline_evaluation.ipynb](./baseline_evaluation.ipynb) and its downloaded output folders are historical diagnostic runs. Use the prepared-data baseline above for the next fine-tuning comparison. [training_token_audit.ipynb](./training_token_audit.ipynb) records the sequence-length investigation.

The saved data and diagnostics contain clinical text. JSON validity and exact value matching do not establish clinical correctness. Preparation does not detect near-duplicate cases or patient-level leakage, and the reused validation cases are a development comparison set, not an untouched final test set.

A separate command-line pipeline is documented in [CLINICAL_PIPELINE.md](./CLINICAL_PIPELINE.md). Its artifact format and preparation protocol differ from these notebooks; do not feed the notebook exports to those scripts or mix their evaluation results. The notebook baseline and subsequent notebook training must use the same notebook-prepared version.
