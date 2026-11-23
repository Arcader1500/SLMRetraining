# Experiment and audit catalog

Recorded progression; frozen artifact locations remain stable.

| Run | Scope | Status / evidence |
| --- | --- | --- |
| Token audit / baseline | First 1,500 training candidates; early baseline | Historical [token audit](../../archive/runs/training_token_audit/), [baseline](../../archive/runs/baseline_evaluation/), [10-case diagnostic](../../archive/runs/baseline_evaluation_diagnostic_10/) |
| V1 pilot 01 | 1,325 train / 10 validation; short LoRA pilot | [Training](../../archive/runs/pilot_01/), [checks](../../archive/runs/pilot_01_checks/), [comparison](../../archive/runs/pilot_01_comparision/); validation loss 0.4452 |
| V1 pilot 02 | Same v1 data; one epoch | [Training](../../archive/runs/pilot_02/), [comparison](../../archive/runs/pilot_02_comparision/); validation loss 0.3793 |
| Decoding ablation | Ten historical cases | [Saved ablation](../../archive/runs/decoding_ablation_10/); separate from current contract |
| V2 full-schema | 1,325 train / 30 development; 3 epochs, 498 steps | Complete [v2 results](../../results_v2/README.md); generated-only 1.08: raw JSON 28/30, strict F1 18.93%, soft F1 30.74% |
| V2 source audit / candidate scan | 30 v2 adapter outputs; separate 100k dataset scan | [Archived audit](../../archive/docs/v2/EXTRACTION_AUDIT_2026-11-17.md); source/reference defects; candidate revision had only 15 unique prompt-answer pairs |
| V3 reduced-schema | Same 1,325 training IDs; 100 new development cases; 3 epochs, 498 steps | Complete [protocol](REDUCED_SCHEMA_1325_RUN.md), [results](../../results_v3/README.md); raw JSON 95/100, allowed schema 87/100, strict F1 26.04%, soft F1 41.44% |
| Reference-only judge | 20 v3 cases, 80 measurements | Complete `a6bb10a9fde5e2b4`; fidelity 0.335/0.375, coverage 0.410/0.455 (base/adapter) |
| Source diagnostic audit | Same 20 paired cases | Complete [report](../../results_v3/source_audit_20/REPORT.md); 160 selected probes, not exhaustive error rates |
| Source judge, first 20 | Same outputs, changed truth source/rubric; 80 measurements | Complete `d44ef976ae8d9310`; fidelity 0.355/0.460, coverage 0.370/0.470 |
| Source judge, remaining 80 | Complement of first 20; 320 new measurements | Complete `16727c1bd7aaf775`; [combined 100-case summary](../../results_v3/deepeval_remaining80/judgments/16727c1bd7aaf775/combined_summary_100.json): fidelity 0.386/0.516, coverage 0.407/0.502 |
| Training-label audit | All-row structure/projection; frozen 50 random + 50 targeted sample | **Complete (100/100):** [Completion report](../../results_v3/training_audit_100/continuation_v2/REPORT.md), [case ledger](../../results_v3/training_audit_100/continuation_v2/combined_case_ledger.json); all 22 integrity checks passed |
| V2 / 5,000 full-schema | 5,000 train / same 100 frozen validation; 3 epochs, 1,875 steps | **Complete:** Dataset `3f8f10951130896b`; [results](../../results_v2_5000/README.md); raw JSON 96/100, strict F1 24.79%, soft F1 40.67%; `gpt-6-luna` fidelity 0.409→0.517, coverage 0.450→0.526; `gemini-4-hydrogen` fidelity 0.386→0.539, coverage 0.412→0.550 |
| Tier 1 diagnostics & V3 label regeneration | 1,325 train + 100 validation (`gemini-3.8-flash` + programmatic repair) | **Complete & packaged:** Dataset [ca7b6e90c1019441](../../prepared_clinical_dataset/ca7b6e90c1019441/manifest.json); diagnostics in [tier1_offline_diagnostics.json](../../prepared_clinical_dataset/v3_regenerated_gemini_3_8_flash/tier1_offline_diagnostics.json) and [final_verification_report.json](../../prepared_clinical_dataset/v3_regenerated_gemini_3_8_flash/final_verification_report.json); ready for SFT training |

Compare models within a frozen protocol. Cross-version and cross-rubric changes are not additional controlled model gains. Semantic results are source-consistency assessments, not clinician adjudication. Historical directory spellings remain unchanged because saved artifacts reference them.
