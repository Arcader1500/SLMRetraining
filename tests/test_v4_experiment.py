"""Offline verification tests for the v4 (ca7b6e90c1019441) training and evaluation pipeline."""
import json
import unittest
from pathlib import Path

from scripts.build_v4_notebooks import (
    FROZEN_20_CASES,
    ROOT,
    build_notebooks,
    digest,
    evaluate_output,
    find_schema_violations,
    prepare_baseline,
)
from scripts.prepare_v3_dataset import schema_valid


class TestV4Experiment(unittest.TestCase):
    def test_dataset_manifest_and_masks(self):
        pointer = json.loads((ROOT / "prepared_clinical_dataset/latest_v3_regenerated.json").read_text(encoding="utf-8"))
        self.assertEqual(pointer["version"], "ca7b6e90c1019441")
        pdir = ROOT / "prepared_clinical_dataset" / pointer["version"]
        manifest = json.loads((pdir / "manifest.json").read_text(encoding="utf-8"))
        train_rows = [json.loads(line) for line in (pdir / "train.jsonl").read_text(encoding="utf-8").split("\n") if line.strip()]
        val_rows = [json.loads(line) for line in (pdir / "validation.jsonl").read_text(encoding="utf-8").split("\n") if line.strip()]
        self.assertEqual(len(train_rows), 1325)
        self.assertEqual(len(val_rows), 100)
        self.assertEqual(digest(train_rows), manifest["split_sha256"]["train"])
        self.assertEqual(digest(val_rows), manifest["split_sha256"]["validation"])

        # Verify zero normalized note overlap and valid label masks & schema on all 1,425 rows
        train_notes = {r["note_sha256"] for r in train_rows}
        val_notes = {r["note_sha256"] for r in val_rows}
        self.assertFalse(train_notes & val_notes)

        for split_name, rows in (("train", train_rows), ("validation", val_rows)):
            for row in rows:
                ids, mask, labels = row["input_ids"], row["attention_mask"], row["labels"]
                self.assertEqual(len(ids), len(mask))
                self.assertEqual(len(ids), len(labels))
                self.assertLessEqual(len(ids), 2048)
                first_ans = next(i for i, v in enumerate(labels) if v != -100)
                self.assertEqual(labels[:first_ans], [-100] * first_ans)
                self.assertEqual(labels[first_ans:], ids[first_ans:])
                self.assertTrue(schema_valid(json.loads(row["reference"])), f"Invalid schema in {row['case_id']}")

    def test_baseline_and_notebooks_build_and_compile(self):
        contract = prepare_baseline(ROOT)
        self.assertEqual(contract["dataset_version"], "ca7b6e90c1019441")
        self.assertEqual(len(contract["case_ids"]), 100)
        self.assertTrue(set(FROZEN_20_CASES).issubset(set(contract["case_ids"])))

        # Verify frozen 20 cases match deepeval_20/selection_manifest.json
        sel20 = json.loads((ROOT / "results_v3/deepeval_20/selection_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(FROZEN_20_CASES, sel20["case_ids"])

        dest = build_notebooks(ROOT)
        for name in ("01_baseline_eval.ipynb", "02_finetune.ipynb", "03_eval_and_compare.ipynb"):
            nb_path = dest / name
            self.assertTrue(nb_path.is_file())
            nb = json.loads(nb_path.read_text(encoding="utf-8"))
            code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
            self.assertGreaterEqual(len(code_cells), 4)
            for idx, c in enumerate(code_cells):
                src = "".join(c["source"])
                if not src.startswith("%"):
                    compile(src, f"{name}:cell_{idx}", "exec")

        # Verify 02_finetune has checkpoint retention and 498 steps assertion
        nb02_text = (dest / "02_finetune.ipynb").read_text(encoding="utf-8")
        self.assertIn("global_step == 498", nb02_text)
        self.assertIn("SaveLiveLog", nb02_text)
        self.assertNotIn('shutil.rmtree(OUTPUT_DIR / "checkpoints")', nb02_text)

        # Verify 03_eval_and_compare has both 100-case evaluation and 20-case gen_rp_1.00 ablation for v3 and v4
        nb03_text = (dest / "03_eval_and_compare.ipynb").read_text(encoding="utf-8")
        self.assertIn("finetuned_v3__gen_rp_1.00_20", nb03_text)
        self.assertIn("finetuned_v4__gen_rp_1.00_20", nb03_text)
        self.assertIn("ablation_20_decoding_comparison.csv", nb03_text)

    def test_schema_violations_helper(self):
        ref = json.dumps({
            "visit motivation": "None", "admission": [], "patient information": {},
            "patient medical history": {}, "surgeries": [], "symptoms": [],
            "medical examinations": [], "diagnosis tests": [], "treatments": [], "discharge": {},
        })
        cases = [{"case_id": "validation:1", "reference": ref}, {"case_id": "validation:2", "reference": ref}]
        outputs = {
            "validation:1": ref,
            "validation:2": json.dumps({**json.loads(ref), "surgeries": [{"Type": "A", "result": "bad"}]}),
        }
        violations = find_schema_violations(cases, outputs)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["case_id"], "validation:2")
        self.assertIn("surgeries[0]: disallowed key result", violations[0]["issues"])


if __name__ == "__main__":
    unittest.main()
