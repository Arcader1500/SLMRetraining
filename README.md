# Clinical JSON extraction fine-tuning

Reproducible FP32 LoRA experiments with `google/gemma-3-270m-it`, extracting notes into ten-section JSON. The current experiment is **v3: 1,325 training examples, a reduced 30-path schema, and 100 frozen development cases**.

Start with the [session handoff](docs/SESSION_HANDOFF.md), [documentation index](docs/README.md), and [run catalog](docs/experiments/RUN_CATALOG.md).

## Current results

| Same 100 development cases | Base | Fine-tuned v3 |
| --- | ---: | ---: |
| Raw-valid JSON | 0/100 | 95/100 |
| Allowed keys and types | 0/100 | 87/100 |
| Mean strict reference fact F1 | 2.98% | 26.04% |
| Mean soft reference fact F1 | 5.17% | 41.44% |
| Source fidelity, LLM rubric | 0.386 | 0.516 |
| Source coverage, LLM rubric | 0.407 | 0.502 |

Generation and all 400 source-rubric measurements are complete. These are development results against synthetic references and LLM source-consistency judgments, not clinician-adjudicated accuracy. The [training-label audit](results_v3/training_audit_100/REPORT.md) has reviewed **10 of 100** sampled cases; 90 remain. The proposed 5,000-example experiment has not started.

## Repository map

| Location | Purpose |
| --- | --- |
| [clinical_sft/](clinical_sft/) | Separate standalone CLI pilot pipeline |
| [scripts/](scripts/README.md) | Preparation, evaluation, audit, report and Colab tools |
| [notebooks/](notebooks/README.md) | Current v3 and preserved v2 workflows |
| [prepared_clinical_dataset/](prepared_clinical_dataset/README.md) | Frozen datasets, cleaning logs and manifests |
| [results_v3/](results_v3/README.md) | Current training, generation, semantic evaluation and audits |
| [results_v2/](results_v2/README.md) | Preserved full-schema 30-case experiment |
| [docs/](docs/README.md) | Current handoff, guides, protocols and report |
| [archive/](archive/README.md) | Older docs, planning evidence, prompts, notebooks and pilots |
| [tests/](tests/) | Offline unit tests |

Frozen artifact paths and provenance-hashed execution sources stay stable. Current and historical artifacts are cataloged without rewriting saved predictions, labels or contracts.

## Run and verify

The primary workflow is [notebooks/v3_1325/](notebooks/v3_1325/), in numbered order. See the [experiment protocol](docs/experiments/REDUCED_SCHEMA_1325_RUN.md) and [dataset/cleaning guide](docs/data/README.md). Preparation requires the ML dependencies and Hugging Face access to Gemma; model execution needs a suitable GPU. The project `pyproject.toml`/`uv.lock` describe a different dependency stack from the recorded Colab runs; use notebook setup cells for reproduction.

The separate CLI workflow uses [requirements-clinical.txt](requirements-clinical.txt) and its [guide](docs/guides/CLINICAL_PIPELINE.md). Its data and contracts are not interchangeable with notebook artifacts. Judge dependencies are isolated in [requirements-deepeval.txt](requirements-deepeval.txt); execution requires explicit runner flags. Gemini remains disabled.

From the repository root, offline checks require no GPU or model downloads:

```bash
python -m unittest discover -s tests -v
python -m scripts.check_remaining_validation
```

On this Windows workspace, use `.venv/Scripts/python.exe` if the system Python alias is unavailable.
