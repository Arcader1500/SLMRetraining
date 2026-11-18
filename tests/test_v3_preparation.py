import copy
import unittest

from scripts.prepare_v3_dataset import SCHEMA, DICT_KEYS, project, schema_valid


class ReducedSchemaTests(unittest.TestCase):
    def example(self):
        return {k: "None" if k == "visit motivation" else {} if k in DICT_KEYS else [] for k in SCHEMA}

    def test_projection_preserves_negation_events_and_input(self):
        obj = self.example()
        obj["symptoms"] = [{"name of symptom": "No fever", "intensity": "absent"}, {"intensity": "mild"}]
        obj["treatments"] = [{"dosage": "5 mg", "frequency": "daily"}, {"dosage": "5 mg", "frequency": "weekly"}]
        original = copy.deepcopy(obj)
        result = project(obj)
        self.assertEqual(obj, original)
        self.assertEqual(result["symptoms"], [{"name of symptom": "No fever"}])
        self.assertEqual(len(result["treatments"]), 2)
        self.assertEqual(set(result), set(SCHEMA))
        self.assertEqual(len(SCHEMA) + sum(map(len, SCHEMA.values())), 30)

    def test_schema_rejects_extra_keys_bad_shapes_and_nested_values(self):
        obj = self.example()
        self.assertTrue(schema_valid(obj))
        for invalid in [None, [], {**obj, "extra": {}}, {**obj, "symptoms": {}},
                        {**obj, "treatments": [{"frequency": "daily"}]},
                        {**obj, "treatments": [{"name": {"nested": "value"}}]}]:
            self.assertFalse(schema_valid(invalid))


if __name__ == "__main__":
    unittest.main()
