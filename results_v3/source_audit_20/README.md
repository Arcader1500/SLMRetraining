# Source audit: completed 20-case review

**Current status, 18 November 2026:** all 20 cases are reviewed. Start with
[REPORT.md](REPORT.md) and [CASE_LEDGER.md](CASE_LEDGER.md). Completed artifacts:
`audit.json`, `reviewed_annotations.json`, `probes.csv`, `findings.csv`,
`reference_and_judge_concerns.csv`, `field_outcomes.csv`, `summary.json`,
`validation_checks.json` and `reconciliation_log.json`. There are 160 probes,
104 model findings, 23 reference concerns and 29 judge concerns. These are
diagnostic ledger counts, not exhaustive error rates. Original draft annotations
and the index below are preserved. Rebuild with `complete_annotations.py`, then
`build_report.py`, using the workspace Python. No inference or training ran.

## Historical draft handoff (superseded by the completed report)

Paused at the user's request so a fresh chat can finish. This is an assistant
source-consistency review, not clinician adjudication or a completed gold set.
No new model inference, judge calls or training were performed for this audit.

## Saved state

- `annotations.json`: **12 provisional case reviews**, 96 source-supported fact
  probes, 61 model findings, 15 reference concerns and 15 judge concerns.
- `indexed_inputs.json`: all 20 notes with indexed scalar leaves from references
  and both outputs. This preserves the evidence IDs used in the annotations.
- `progress.json`: draft IDs, remaining IDs and verification status.
- Original notes/references/raw outputs remain in
  `results_v3/deepeval_20/paired_cases.json`; never overwrite them.

The eight remaining cases are `validation:412`, `validation:2654`,
`validation:1133`, `validation:1628`, `validation:1722`, `validation:2890`,
`validation:435` and `validation:337`. The first four were inspected during the
interrupted session but **have no saved annotations**; read them again.

All source quotes in the 12 saved drafts passed an exact substring check against
their notes. Four Unicode-corrupted quotes were corrected with explicit Unicode
escapes before this check. **This verifies quote existence, not the correctness
of the semantic labels.** No aggregate audit rates have been produced.

## Draft annotation format

Each case contains four lists:

| List | Row layout |
| --- | --- |
| `probes` | `[field, fact description, exact note quote, baseline outcome, fine-tuned outcome]` |
| `findings` | `[baseline or finetuned, primary category, evidence, exact note quote, explanation]` |
| `reference_review` | `[concern category, reference evidence, exact note quote, explanation]` |
| `judge_review` | `[concern category, exact note quote, explanation]` |

Outcome notation is `STATUS:EVIDENCE`, or `O` for omitted. Draft statuses:

- `S`: supported, with an appropriate clinical field/event role.
- `P`: source fact present, but in an inappropriate clinical role/field.
- `C`: contradicted, wrong value or wrong entity/event relation.
- `X`: both correct and inconsistent versions occur.
- `O`: omitted from the readable output.
- `A`: ambiguous; do not force it into correct or incorrect.

Evidence such as `B14 B15`, `F03` or `R07` refers to baseline, fine-tuned or
reference leaf IDs in `indexed_inputs.json`. A value beginning with `@` is an
exact raw-output substring, used when parsing fails or text occurs in an array
not recovered by the diagnostic index. Example: `P:@two seizure-like episodes
earlier that morning`.

**Decide and apply a consistent field-role policy before counting.** Draft labels
may overclassify placement: a procedure described accurately in history/discharge
can preserve the clinical event even if it misses the preferred schema slot.
Do not treat synonymous parent spelling as a semantic error automatically;
existing strict schema metrics already measure that. Cross-check ambiguous cases
and all `S/P/C/X` decisions before publishing counts.

## Diagnostic-index limits

Parseable output is flattened into leaves. Exact repeated `(path with array
indices normalized, value)` leaves are collapsed with occurrence counts. Full
outputs remain untouched.

For unparseable outputs the index extracts only recognizable scalar key/value
spans. **It misses array strings and unterminated strings.** In particular:

- Baseline 2654 is essentially an unclosed quoted copy of the note; its leaf
  index is empty even though much supported source content is readable.
- Baseline 1388 has seizure descriptions in arrays that the index misses.
- Baseline 2890 has long source excerpts in `Symptoms` arrays that the index
  misses. Do not classify those facts as omitted without reading raw text.
- Baseline 1812 and 1628 have invalid unit-bearing scalars; numeric regex spans
  are incomplete and must be checked in raw context.
- Fine-tuned 1953, 1133 and 435 are malformed repeated outputs. Review readable
  prefixes, but never upgrade their whole-object parse validity or repair them
  into passing predictions.

## Remaining work

1. Complete eight cases, aiming for eight explicit source-fact probes per case
   plus model/reference/judge findings. This is a diagnostic probe set, not an
   exhaustive inventory of every clinical fact or model assertion.
2. Validate exact note quotes, evidence IDs/raw excerpts, source hashes and all
   outcome labels. Resolve role-versus-omission and relation-versus-placement
   inconsistencies in the first 12 drafts.
3. Save a structured audit JSON, probe/outcome CSV, findings CSV and readable
   case-by-case Markdown report. A formatter/validator has **not** been written.
4. Report probe outcomes by field and model, with demographic versus clinical
   probes separated. Report confirmed finding counts and affected-case counts
   by category. Do not call these exhaustive error rates, claim-level precision
   or recall; no full denominator of all source/model claims has been annotated.
5. Separate clear reference errors, omissions, temporal/causal ambiguity and
   annotation-policy concerns. Keep judge criticisms distinct from verified
   model errors. Fifteen reference concerns do not mean fifteen clear defects.
6. Derive training priorities and small controlled experiments from the finished
   audit. Do not add these development cases to training.
