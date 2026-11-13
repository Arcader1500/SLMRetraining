import json
from pathlib import Path
import tempfile
import unittest

from clinical_sft.common import (clean_reference, clinical_values, encode_example,
                                 FORMAT_INSTRUCTION, file_hash, pad_examples,
                                 score_response, verify_data, write_json)


class CharacterTokenizer:
    """Each character is a token, making assistant boundaries independently visible."""

    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=False):
        text = "".join(f"<{m['role']}>" + m["content"] + "<end>" for m in messages)
        return text + ("<assistant>" if add_generation_prompt else "")

    def __call__(self, text, **kwargs):
        return {"input_ids": [ord(c) for c in text], "attention_mask": [1] * len(text),
                "offset_mapping": [(i, i + 1) for i in range(len(text))]}


class ClinicalPipelineTests(unittest.TestCase):
    def test_control_character_repair_preserves_value(self):
        cleaned, status = clean_reference('{"note":"first\nsecond\tline"}')
        self.assertEqual(status, "escaped_control_characters")
        self.assertEqual(json.loads(cleaned)["note"], "first\nsecond\tline")
        self.assertIn("\\n", cleaned)

    def test_ambiguous_syntax_is_not_repaired(self):
        for text in ('{"a":1,}', '{"a":"broken}', '{"a":1 "b":2}', '{"a":1,"a":2}',
                     '{"a":NaN}', '[]', '{}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                clean_reference(text)

    def test_mask_covers_prompt_but_keeps_complete_answer_and_terminator(self):
        answer = '{"age":"29"}'
        row = encode_example(CharacterTokenizer(), {"system": "extract", "note": "29yo", "reference": answer})
        first = next(i for i, label in enumerate(row["labels"]) if label != -100)
        self.assertGreater(first, 0)
        self.assertEqual(row["labels"][:first], [-100] * first)
        self.assertEqual("".join(chr(i) for i in row["labels"][first:]), answer + "<end>")

    def test_pad_id_equal_to_eos_does_not_hide_real_end_label(self):
        batch = pad_examples([{"input_ids": [5, 1], "labels": [-100, 1]},
                              {"input_ids": [5, 6, 1], "labels": [-100, 6, 1]}], 1)
        self.assertEqual(batch["input_ids"][0], [5, 1, 1])
        self.assertEqual(batch["labels"][0], [-100, 1, -100])
        self.assertEqual(batch["attention_mask"][0], [1, 1, 0])

    def test_placeholders_cannot_score_as_extracted_facts(self):
        result = score_response('{"age":"None"}', '{"age":"29"}')
        self.assertTrue(result["exact_key_match"])
        self.assertEqual(result["value_f1"], 0)
        self.assertEqual(result["non_placeholder_values"], 0)

    def test_value_comparison_is_field_specific_and_handles_fences(self):
        reference = '{"age":"29","sex":"female"}'
        self.assertEqual(score_response('```json\n' + reference + '\n```', reference)["value_f1"], 1)
        self.assertEqual(score_response('{"age":"female","sex":"29"}', reference)["value_f1"], 0)
        self.assertFalse(score_response('truncated {', reference)["valid_json"])
        self.assertEqual(clinical_values({"age": None}), set())

    def test_duplicate_generated_keys_are_invalid(self):
        self.assertFalse(score_response('{"a":"1","a":"2"}', '{"a":"1"}')["valid_json"])

    def test_prepared_data_and_prompt_are_frozen(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            write_json(path / "train.json", [{"value": 1}])
            manifest = {"format_instruction": FORMAT_INSTRUCTION,
                        "files": {"train.json": file_hash(path / "train.json")}}
            write_json(path / "manifest.json", manifest)
            self.assertEqual(verify_data(path), manifest)
            write_json(path / "train.json", [{"value": 2}])
            with self.assertRaises(ValueError):
                verify_data(path)
            manifest["format_instruction"] = "changed"
            write_json(path / "manifest.json", manifest)
            with self.assertRaises(ValueError):
                verify_data(path)


if __name__ == "__main__":
    unittest.main()
