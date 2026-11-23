Your methodology is already far ahead of most SLM fine-tuning projects—especially auditing the 100k dataset, masking prompts, catching greedy-loop attractors, and doing source-grounded error audits. Because your syntax is essentially solved (`95–96%`), **semantic binding and event status** are now the entire game.

Below are the biggest blind spots in the current setup, followed by concrete levers across architecture, training techniques, and distillation—prioritized by impact on binding errors.

---

## 1. Blind Spots You May Be Missing

### A. Gemma-3 270M's 512-Token Sliding Window & 100M Transformer Body

Two architectural facts about `google/gemma-3-270m-it` directly explain why demographics (`38/40`) work while late-section drug/test binding breaks down:

* **Only 3 of 18 layers can see beyond 512 tokens:** Gemma-3 270M has 18 layers in a **5:1 local-to-global** pattern, where the 15 local layers use a `512`-token sliding window. Furthermore, every attention layer uses **1 KV head** (4 query heads, MQA). When your prompt plus partial JSON exceeds 512 tokens—which happens routinely on `1,651`-token sequences—15 layers literally cannot attend back to the clinical note while generating `diagnosis tests`, `treatments`, and `discharge`. Only 3 single-KV-head layers carry all long-range entity binding.
* **Most of the 270M parameters are embeddings:** With a `262,144` vocabulary and `hidden_size=640`, roughly `168M` parameters live in the tied embedding table, leaving **only ~100M parameters** in the actual transformer body.

**Diagnostic test to run immediately:** Stratify your existing binding errors by (1) **JSON section position** (early vs. late sections) and (2) **token distance** between the source mention and the generated JSON field. If errors spike past ~512 tokens, label cleanup alone will hit a hard architectural ceiling.

### B. `gen_rp=1.08` Is Likely Causing Entity Swaps

Applying a uniform repetition penalty (`1.08`) to all generated tokens fixed your loops, but it introduces a subtle bias in multi-section clinical JSON: **legitimate tokens must repeat** across sections (drug names, modalities like `CT` or `biopsy`, units like `mg`, status words). Once `CT` or `Drug A` appears in `admission` or `medical examinations`, `gen_rp=1.08` penalizes emitting it again in `diagnosis tests` or `treatments`—nudging greedy decoding to pick `MRI` or `Drug B` instead.

**Diagnostic test:** On the `95%` of cases that do **not** hit the 2,048-token budget, compare binding error rates at `gen_rp=1.00` vs. `1.08`.

### C. The `91%` Truncated Source Notes Problem

`1,206/1,325` notes lacking terminal punctuation is a major hidden risk while you regenerate labels:

* **Distribution mismatch:** Verify whether your real downstream inference notes are truncated or complete. Training on 91% mid-word-truncated inputs teaches abnormal completion/EOS behavior.
* **Label regeneration leakage:** When regenerating labels, ensure the teacher model sees **only the raw visible note** (never the original synthetic reference) and has an explicit rule to leave `discharge`/outcome empty if the note cuts off before that event.
* **Auditor fallibility = teacher fallibility:** Since `gpt-6-luna` had a ~30% reject/downgrade rate on second-pass audit (`69/226`), single-pass LLM regeneration will bake new systematic noise into your labels unless gated by deterministic checks (more in Section 4).

### D. Why Fine-Tuning Increased Wrong Relations (`1 → 7`)

Cutting omissions (`19 → 11`) while increasing misbindings (`11 → 20`) is classic **over-extraction under noisy SFT**: the base model was conservative, whereas SFT heavily rewards populating slots. Because the noisy labels lacked clean alignment and the model's attention capacity is tight, trying harder to fill every slot produces cross-wired attributes.

---

## 2. High-ROI Changes to Schema, Inference & SFT

Before jumping to complex RL or white-box distillation, four structural adjustments attack your exact failure modes directly:

1. **Evidence-First JSON Ordering (Hacks Around the 512-Token Window)**
Add a short verbatim `"evidence"` string as the **first key** inside each `diagnosis_test`, `surgery`, and `treatment` object—copied directly from the note *before* extracting `dose`, `result`, or `status`:
```json
{
  "evidence": "declined CT-guided biopsy; underwent VATS biopsy showing CK7+",
  "test": "VATS biopsy",
  "status": "performed",
  "result": "CK7+"
}

```


Autoregressively emitting the 8–15 word source span pulls the exact clinical facts **back inside the 512-token local sliding window** for all 15 local layers right before the model binds the fields. You can strip `"evidence"` in post-processing and also use it as a deterministic hallucination filter (check substring overlap against the source note).
2. **Explicit `status` Enum on Clinical Events**
Instead of expecting a 100M-body model to implicitly separate performed vs. planned vs. refused procedures, add a mandatory constrained enum: `"status": "performed" | "planned" | "refused" | "negated" | "historical"`. This turns an implicit omission problem into an explicit classification decision.
3. **Multi-Pass Extraction with Shared Prompt KV-Cache**
Split the 10-section schema into **2 or 3 short focused passes** (e.g., Pass 1: Demographics/History/Admission/Symptoms; Pass 2: Exams/Diagnostic Tests; Pass 3: Surgeries/Treatments/Discharge). At inference, engines like `vLLM` or `llama.cpp` reuse the prompt KV-cache across passes, so latency barely increases, while every generated output stays well under 512 tokens—keeping the clinical note in range and virtually eliminating 2,048-token loops.
4. **Grammar-Constrained Decoding + Full Fine-Tuning + Value-Weighted Loss**
* **Constrained decoding (`xgrammar`, `llguidance`, or `outlines`):** Guarantees `100%` JSON syntax and key/enum compliance at inference time, eliminating the remaining `4–5%` parse errors and `8` schema violations—and lets you drop `gen_rp=1.08` (replace with a targeted n-gram loop breaker or schema max-array-length cap).
* **Full Fine-Tuning vs. `r=16` LoRA:** On a 270M model (`~100M` transformer body), `r=16` LoRA leaves the base attention projections and `lm_head` largely rigid. Full FT in `FP32` with gradient checkpointing + 8-bit AdamW easily fits inside your `15 GiB` T4 (`~6–8 GiB` VRAM) and frequently outperforms LoRA on fine-grained attention routing in sub-1B models. Run a clean A/B (`lr=3e-5` to `5e-5` cosine) once your regenerated labels are ready.
* **Upweight leaf value tokens in SFT loss:** Standard cross-entropy spends a huge fraction of gradient on JSON punctuation and schema keys. Weighting leaf-value tokens `2×–3×` higher than structural/key tokens focuses limited capacity on binding `dose`, `result`, and `status`.



---

## 3. Training Techniques Beyond SFT

Once you have clean, verified labels and a solid SFT baseline, two post-training methods directly target semantic binding—something standard SFT struggles with because SFT never explicitly penalizes "almost right, wrong drug."

### Surgical Hard-Negative DPO / SimPO

Instead of generic preference data, build **minimal-edit contrastive pairs** directly from your clean regenerated labels (`chosen`) and programmatically corrupted variants (`rejected`) targeting your exact audit errors:

* **Drug–attribute swap:** Swap `dose`, `frequency`, or `response` between two entries in `treatments`.
* **Test–result swap:** Swap `result` between two `diagnosis tests` (e.g., CT vs. MRI).
* **Status inversion:** Flip a `refused` or `planned` event to `performed`, or move a historical condition into the current visit.
* **Truncation hallucination:** Append a plausible-sounding `discharge` field on a truncated note.
* **On-policy negatives:** Include real binding mistakes generated by your SFT checkpoint (flagged by your verifier) paired against the clean label.

Train with **DPO + NLL anchor (RPO / MPO)** or **SimPO** for 1–2 epochs at a low learning rate (`5e-6` to `1e-5`). The NLL anchor term (`beta * DPO_loss + alpha * SFT_loss`) is critical on small models so JSON formatting doesn't drift while binding sharpens.

### RLVR / GRPO (Verifiable-Reward RL)

On a 270M model, **GRPO** (Group Relative Policy Optimization) is surprisingly cheap and directly addresses **exposure bias** (the mismatch between teacher-forced training and autoregressive generation that causes loops and over-extraction). For each note, sample $G = 4\text{–}8$ rollouts and compute a deterministic composite reward:

1. Hard gate (`0.0` if invalid JSON or schema violation).
2. Verbatim grounding score (fraction of extracted `evidence` spans and numeric dosages/units present in the source note).
3. Structured tuple-matching F1 against your verified clean labels (scoring `(entity, attribute, status)` tuples rather than flat strings).
4. Length/repetition penalty for runaway arrays.

---

## 4. Distillation: What's Worth Doing (and When)

"Distillation" covers two very different pipelines with very different ROI on a Tesla T4:

### 1. Verified Sequence-Level Distillation (Do This Now)

What you have started—regenerating labels from a stronger teacher—is black-box sequence-level distillation. To avoid replacing one noisy label set with another, add a **3-step verification pipeline** around generation:

1. **Generate** with evidence spans + explicit `status` enums from your strongest available teacher (with the prompt strictly banning completions past truncated text).
2. **Programmatically verify** every label: schema check + fuzzy substring check confirming every `evidence` span, number, dosage, and test name exists in the source note.
3. **Adjudicate/Filter** failed rows (either re-prompt the teacher with the exact verification failure, or drop unverified rows rather than poisoning training).

### 2. White-Box Logit KD & On-Policy Distillation (GKD) (Do Later, Only If Needed)

Logit distillation (`KL(P_teacher || P_student)`) requires **matching tokenizers**, meaning your natural white-box teachers for `gemma-3-270m-it` are **`gemma-3-12b-it`** or **`gemma-3-27b-it`**.

* **How to run it on a T4:** You don't need the teacher in VRAM during student training. Run one offline pass on a rented larger GPU to cache the teacher's **top-32 or top-64 logprobs** per target token, then train your 270M student on the T4 using a blended `CE + KL` loss.
* **Critical detail—use Reverse KL or Skewed JSD, not Forward KL:** Forward KL forces a tiny 100M-body student to spread probability mass over all modes of the teacher ("mode covering"), which blurs confidence between competing entities. **Reverse KL** or **Generalized Knowledge Distillation (GKD)** (scoring the *student's own generated tokens* with the teacher) sharpens mode-seeking behavior and directly repairs exposure bias.

### Recommended Priority Order

| Priority | Lever | Target Failure Mode | Effort |
| --- | --- | --- | --- |
| **1** | **Programmatically verified label regeneration** + truncation hygiene + small human-adjudicated gold set (30–50 cases) | Noisy supervision & noisy eval | Medium |
| **2** | **Diagnose 512-token window & `gen_rp=1.08**` on existing outputs; switch to **constrained decoding** | Entity swaps, parse errors, loops | Low |
| **3** | **Evidence-first schema + explicit `status` enum** (or 2–3 pass KV-cached split) | Drug/test misbinding, planned vs. performed | Low–Med |
| **4** | **Full FT vs. LoRA A/B** + value-weighted SFT loss (and optional base-model check against a full-attention 0.5B–1B SLM) | Capacity & global attention routing | Low–Med |
| **5** | **Surgical Hard-Negative DPO (with NLL anchor)** or **GRPO** | Remaining relation swaps & exposure bias | Medium |
| **6** | **Offline Top-$K$ Reverse-KL / On-Policy GKD** from Gemma-3 12B/27B | Final 2–5% accuracy squeeze | High |

One final sanity check on your base model constraint: if your deployment budget allows `0.5B–1B` (or even `360M–600M` with full global attention and a smaller vocab so more weights sit in the transformer body rather than embeddings), run one quick baseline comparison on your cleaned dataset before committing weeks to post-training a 100M-body 512-window architecture.