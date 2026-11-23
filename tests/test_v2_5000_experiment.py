"""Offline checks for full-schema retention, fixed pairs and bounded judge resume."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.prepare_v2_5000_dataset import extend_training, prepare_row
from scripts.prepare_v2_dataset import TOP_LEVEL_KEYS, DICT_KEYS
from scripts.run_deepeval import evaluate
from scripts.source_grounded_rubric import METRIC_STEPS, VERSION


class CharacterTokenizer:
    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=False):
        return messages[0]["content"] + "ASSISTANT:" + (messages[1]["content"]+"END" if len(messages) > 1 else "")
    def __call__(self, text, **kwargs):
        return dict(input_ids=list(range(len(text))), offset_mapping=[(i, i+1) for i in range(len(text))])


class ExperimentTests(unittest.TestCase):
    def test_preserve_full_v2_fields_and_prompt_mask(self):
        target = {k: ("pain" if k == "visit motivation" else {} if k in DICT_KEYS else []) for k in TOP_LEVEL_KEYS}
        target["treatments"] = [dict(name="A", frequency="every 12 hours", duration="7 days", dosage="None")]
        target["diagnosis tests"] = [dict(test="pathology", condition="diagnosis", details="clear margins")]
        raw = dict(messages=[dict(role="system", content="original system"), dict(role="user", content="note"),
                             dict(role="assistant", content=json.dumps(target))])
        row = prepare_row(raw, "train", 3, CharacterTokenizer())
        answer = json.loads(row["reference"])
        self.assertEqual(answer["treatments"], [dict(name="A", frequency="every 12 hours", duration="7 days")])
        self.assertEqual(answer["diagnosis tests"], target["diagnosis tests"])
        self.assertTrue(row["system"].startswith("original system\n\n"))
        first = row["prompt_tokens"]
        self.assertEqual(row["labels"][:first], [-100]*first)
        self.assertEqual(row["labels"][first:], row["input_ids"][first:])

    def test_extend_preserves_original_and_excludes_overlap(self):
        original = [dict(case_id="train:0", note_sha256="a")]
        def candidates():
            for i, key in enumerate(["a", "validation", "b", "c", "d"]):
                yield i, lambda i=i, key=key: dict(case_id=f"train:{i+1}", note_sha256=key, repair="none")
        rows, logs = extend_training(original, candidates(), {"validation"}, target=3)
        self.assertIs(rows[0], original[0])
        self.assertEqual([r["note_sha256"] for r in rows], ["a", "b", "c"])
        self.assertEqual([r["status"] for r in logs], ["rejected", "rejected", "accepted", "accepted"])
        with self.assertRaisesRegex(ValueError, "exactly 5 required"):
            extend_training(original, candidates(), {"validation"}, target=5)

    def test_exact_400_judgments_resume_and_frozen_input_rejection(self):
        # Simulate every case/model/metric without any provider calls.
        pairs = [dict(case_id=f"validation:{i}", input="note", expected_output="{}", baseline_output="base",
                      finetuned_output="adapter", format_metrics=dict(baseline={}, finetuned={})) for i in range(100)]
        count = [0]
        class Metric:
            def __init__(self, name): self.name = name
            def measure(self, case, **kwargs):
                count[0] += 1
                self.score, self.reason = 0.5, "offline fixture"
        def metrics(*args, **kwargs): return [Metric(m) for m in METRIC_STEPS]
        contract = dict(metric_steps=METRIC_STEPS, deepeval_version="4.3.4", rubric_version=VERSION)
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / ".venv") as tmp:
            directory = Path(tmp)/"deepeval_100/judgments/run"
            directory.mkdir(parents=True)
            with patch("scripts.run_deepeval.create_metrics", side_effect=metrics), patch("builtins.print"):
                evaluate(directory, pairs, {}, contract, None, dict(model="gpt-6-luna"), "codex", True, False)
                self.assertEqual(count[0], 400)
                evaluate(directory, pairs, {}, contract, None, dict(model="gpt-6-luna"), "codex", True, False)
                self.assertEqual(count[0], 400)
                summary = json.loads((directory / "summary.json").read_text())
                self.assertTrue(summary["complete"])
                self.assertEqual(summary["measurements"], 400)
                self.assertEqual(summary["selected_cases"], 100)
                pairs[0]["format_metrics"]["baseline"] = dict(changed=True)
                with self.assertRaisesRegex(ValueError, "Checkpoint content"):
                    evaluate(directory, pairs, {}, contract, None, dict(model="gpt-6-luna"), "codex", True, False)


if __name__ == "__main__":
    unittest.main()
