# Preserved v2 results

Historical full-schema run: dataset `eeff5efa1619f198`, 1,325 training / 30 development examples, three epochs and 498 steps of FP32 LoRA on Gemma 270M.

| Folder | Contents |
| --- | --- |
| [baseline/](baseline/) | Frozen selection/contract, base generations under greedy and generated-only penalty 1.08 |
| [finetuned_v2/](finetuned_v2/) | Adapter, runtime/model/label checks, configuration and losses |
| [comparison/](comparison/) | Both adapter decoding conditions, aggregate/case scores and showcase |

Generated-only penalty 1.08 yields 28/30 raw-valid adapter outputs, strict reference F1 18.93%, soft F1 30.74%. V3 uses different schemas/cases. Read the [archived briefing](../archive/docs/v2/TRAINING_AND_EVAL_BRIEFING.md) and [30-case audit](../archive/docs/v2/EXTRACTION_AUDIT_2026-11-17.md). Frozen artifacts remain intact for reproduction and the combined report.
