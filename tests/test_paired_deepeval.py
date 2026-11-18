import copy
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.phase_results import ROOT, load_phase
from scripts.prepare_deepeval import DEFAULT_SETTINGS, METRIC_STEPS, prepare, prepare_remaining
from scripts.run_deepeval import check_backend, run


class PairedEvaluationTests(unittest.TestCase):
    def test_combined_summary_reuses_original_eighty_source_scores(self):
        from scripts.run_deepeval import combine_all_validation
        from scripts.phase_results import read_json
        from scripts.source_grounded_rubric import METRIC_STEPS as source_steps
        with tempfile.TemporaryDirectory(dir=ROOT / '.venv') as folder:
            directory=Path(folder)
            manifest,pairs=prepare_remaining(directory/'selection')
            scores=[dict(case_id=p['case_id'],model=model,metric=metric,score=.5,
                         reason='Offline aggregate test only',format_metrics=p['format_metrics'][model])
                    for p in pairs for model in ('baseline','finetuned') for metric in source_steps]
            combine_all_validation(directory,manifest,scores,source_steps)
            combined=read_json(directory/'combined_scores_100.json')
            original=read_json(ROOT/'results_v3/deepeval_20/judgments/d44ef976ae8d9310/scores.json')
            self.assertEqual(combined[:80],original)
            self.assertEqual(len(combined),400)
            summary=read_json(directory/'combined_summary_100.json')
            for metric in source_steps:
                for model in ('baseline','finetuned'):
                    old=sum(r['score'] for r in original if r['metric']==metric and r['model']==model)
                    self.assertAlmostEqual(summary['mean_scores'][metric][model],(old+40)/100)

    def test_remaining_cases_are_the_exact_frozen_complement(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.venv') as folder:
            manifest,pairs=prepare_remaining(folder)
            self.assertEqual(prepare_remaining(folder),(manifest,pairs))
            original,_=prepare()
            all_ids={c['case_id'] for c in load_phase('phase2')['cases']}
            self.assertEqual(len(pairs),80)
            self.assertEqual(manifest['planned_metric_measurements'],320)
            self.assertFalse(set(manifest['case_ids'])&set(original['case_ids']))
            self.assertEqual(set(manifest['case_ids'])|set(original['case_ids']),all_ids)
            self.assertEqual(manifest['rubric_version'],'source_grounded_v2')

    @unittest.skipUnless(importlib.util.find_spec('deepeval'), 'isolated DeepEval environment required')
    def test_interruption_and_resume_skip_every_saved_measurement(self):
        from scripts.phase_results import read_json
        measurements=[]
        stop={'enabled':True}
        class QuotaError(RuntimeError): kind='usage_limit'
        class Metric:
            def __init__(self,name): self.name=name
            def measure(self,case,**kwargs):
                if stop['enabled'] and len(measurements)==3: raise QuotaError('offline quota simulation')
                measurements.append((case.input,case.actual_output,self.name))
                self.score=.7;self.reason='Offline interruption/resume check, not real judging'
        names=['Source fidelity','Source coverage']
        pairs=[dict(case_id=f'validation:{i}',input=f'note-{i}',expected_output='reference',
                    baseline_output=f'base-{i}',finetuned_output=f'fine-{i}',format_metrics={'baseline':{},'finetuned':{}}) for i in range(2)]
        with tempfile.TemporaryDirectory(dir=ROOT / '.venv') as folder:
            directory=Path(folder)
            settings=copy.deepcopy(DEFAULT_SETTINGS); settings['run_judge']=True
            (directory/'judge_settings.json').write_text(json.dumps(settings),encoding='utf-8')
            with patch('scripts.run_deepeval.prepare_remaining',return_value=({'test':'offline'},pairs)), \
                 patch('scripts.codex_deepeval_judge.CodexJudge',return_value=object()), \
                 patch('scripts.run_deepeval.create_metrics',side_effect=lambda *a,**k:[Metric(n) for n in names]), \
                 patch('scripts.run_deepeval.combine_all_validation'):
                with self.assertRaises(QuotaError):
                    run(directory,execute=True,source_grounded=True,remaining_validation=True)
                out=next((directory/'judgments').iterdir())
                saved=read_json(out/'scores.json')
                self.assertEqual(len(saved),3)
                self.assertEqual(read_json(directory/'progress.json')['failure_kind'],'usage_limit')
                # Simulate a stale progress file and an unfinished temporary score write.
                (out/'progress.json').write_text('{}',encoding='utf-8')
                (out/'scores.pending').write_text('interrupted partial write',encoding='utf-8')
                stop['enabled']=False
                run(directory,execute=True,source_grounded=True,remaining_validation=True)
                after=read_json(out/'scores.json')
                self.assertEqual(after[:3],saved)
                self.assertEqual(len(after),8)
                self.assertEqual(len(measurements),len(set(measurements)))
                self.assertEqual(read_json(directory/'progress.json')['status'],'complete')
                self.assertEqual(read_json(directory/'progress.json')['remaining_measurements'],0)

    def test_frozen_sample_is_shared_and_unfiltered(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".venv") as folder:
            manifest, pairs = prepare(folder)
            self.assertEqual(prepare(folder), (manifest, pairs))
            self.assertEqual(len(set(manifest["case_ids"])), 20)
            self.assertEqual(manifest["paired_test_cases"], 40)
            source = {c["case_id"]: c for c in load_phase("phase2")["cases"]}
            for pair in pairs:
                original = source[pair["case_id"]]
                self.assertEqual(pair["baseline_output"], original["baseline"])
                self.assertEqual(pair["finetuned_output"], original["finetuned"])
                self.assertEqual(pair["expected_output"], original["reference"])
            self.assertTrue(any(p["format_metrics"]["finetuned"]["raw_json_object_valid"] == "False" for p in pairs))
            with self.assertRaises(ValueError):
                prepare(folder, seed=7)

    def test_disabled_gemini_and_codex_first_gate(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        with tempfile.TemporaryDirectory(dir=ROOT / ".venv") as folder:
            with self.assertRaisesRegex(ValueError, "disabled"):
                check_backend(settings, "gemini", folder)
            settings["judges"]["gemini"]["enabled"] = True
            with self.assertRaisesRegex(ValueError, "Complete the Codex"):
                check_backend(settings, "gemini", folder)

    def test_preparation_never_constructs_a_judge(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".venv") as folder:
            with patch("scripts.run_deepeval.create_metrics", side_effect=AssertionError("judge invoked")):
                self.assertIsNone(run(folder, execute=True))
            self.assertFalse((Path(folder) / "judgments").exists())

    @unittest.skipUnless(importlib.util.find_spec("deepeval"), "isolated DeepEval environment required")
    def test_real_deepeval_api_with_offline_stub(self):
        os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"
        os.environ["DEEPEVAL_DISABLE_DOTENV"] = "1"
        from deepeval.models import DeepEvalBaseLLM
        from deepeval.test_case import LLMTestCase
        from scripts.run_deepeval import create_metrics

        class OfflineJudge(DeepEvalBaseLLM):
            def load_model(self): return self
            def get_model_name(self): return "offline-test-only"
            def generate(self, prompt, schema=None):
                return schema(reason="Offline API compatibility test, not an evaluation result", score=8)
            async def a_generate(self, prompt, schema=None): return self.generate(prompt, schema)

        metrics = create_metrics(OfflineJudge())
        self.assertEqual([m.name for m in metrics], list(METRIC_STEPS))
        for metric in metrics:
            metric.measure(LLMTestCase(input="stub", expected_output="stub", actual_output="stub"), _show_indicator=False)
            self.assertAlmostEqual(metric.score, .8)

    @unittest.skipUnless(importlib.util.find_spec("deepeval"), "isolated DeepEval environment required")
    def test_codex_adapter_structured_output_without_model_call(self):
        os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"
        os.environ["DEEPEVAL_DISABLE_DOTENV"] = "1"
        from pydantic import BaseModel
        from scripts.codex_deepeval_judge import CodexJudge

        class Score(BaseModel):
            score: float
            reason: str

        def offline_command(args, **kwargs):
            self.assertIn("--ignore-user-config", args)
            self.assertIn("--ephemeral", args)
            self.assertIn("read-only", args)
            output = Path(args[args.index("--output-last-message") + 1])
            output.write_text('{"score":8,"reason":"offline stub"}', encoding="utf-8")
            schema = json.loads(Path(args[args.index("--output-schema") + 1]).read_text())
            self.assertFalse(schema["additionalProperties"])
            return type("Result", (), {"returncode": 0})()

        with patch("scripts.codex_deepeval_judge.resolve_codex", return_value=["offline-test-only"]):
            with patch("scripts.codex_deepeval_judge.subprocess.run", side_effect=offline_command):
                result = CodexJudge("offline-test-model").generate("offline prompt", Score)
                self.assertEqual(result.score, 8)

    @unittest.skipUnless(importlib.util.find_spec("deepeval"), "isolated DeepEval environment required")
    def test_source_rubric_includes_note_and_preserves_legacy_metrics(self):
        os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"
        from deepeval.models import DeepEvalBaseLLM
        from deepeval.test_case import LLMTestCase
        from scripts.run_deepeval import create_metrics
        from scripts.source_grounded_rubric import METRIC_STEPS as source_steps

        prompts = []
        class OfflineJudge(DeepEvalBaseLLM):
            def load_model(self): return self
            def get_model_name(self): return "offline-source-rubric-test"
            def generate(self, prompt, schema=None):
                prompts.append(prompt)
                return schema(reason="Offline prompt inclusion check", score=8)
            async def a_generate(self, prompt, schema=None): return self.generate(prompt, schema)

        note = "NOTE_SENTINEL: CT biopsy was refused; VATS biopsy showed kappa positivity."
        case = LLMTestCase(input=note, actual_output="CANDIDATE_SENTINEL", expected_output="REFERENCE_SENTINEL")
        for metric in create_metrics(OfflineJudge(), source_grounded=True):
            metric.measure(case, _show_indicator=False)
        self.assertEqual(len(prompts), 2)
        for prompt in prompts:
            self.assertIn(note, prompt)
            self.assertIn("CANDIDATE_SENTINEL", prompt)
            self.assertIn("REFERENCE_SENTINEL", prompt)
            self.assertIn("sole authority", prompt)
            self.assertIn("verbatim Input excerpts", prompt)
        self.assertEqual(len(source_steps), 2)
        self.assertEqual([m.name for m in create_metrics(OfflineJudge())], list(METRIC_STEPS))


if __name__ == "__main__":
    unittest.main()
