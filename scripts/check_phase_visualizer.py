"""Offline browser check for the local report; no external pages or judge calls."""
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []
    external = []
    with sync_playwright() as p:
        chrome = Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe"
        browser = p.chromium.launch(executable_path=str(chrome), headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
        page.on("pageerror", lambda error: errors.append(str(error)))

        def route(request):
            if request.request.url.startswith(("http:", "https:")):
                external.append(request.request.url)
                request.abort()
            else:
                request.continue_()

        page.route("**/*", route)
        page.goto((ROOT / "docs/Clinical_Extraction_Phases_1_and_2.html").as_uri())
        assert page.locator(".phase").count() == 2
        assert page.locator("#metrics-table tr").count() == 4
        runs = []
        if page.locator("#judge-results tbody tr").count():
            data = page.locator('#report-data').text_content()
            runs = [r for r in json.loads(data)['judge_runs'] if r['backend']=='codex']
            assert page.locator("#judge-results tbody tr").count() == 2 * len(runs)
            assert "Complete" in page.locator(".judge .status").first.inner_text()
            if any(r['rubric_version']=='source_grounded_v2' for r in runs):
                assert page.locator('.judge-run').first.get_attribute('data-rubric') == 'source_grounded_v2'
                assert 'Source fidelity' in page.locator('.judge-run').first.inner_text()
                assert 'Source coverage' in page.locator('.judge-run').first.inner_text()
        page.locator("#show-greedy").check()
        assert page.locator("#metrics-table tr").count() == 6
        page.locator("#view-sample").click()
        assert page.locator("#case-id option").count() == 20
        assert page.locator("#case-outputs article").count() == 3
        if runs:
            assert page.locator('#case-judgments > details').count() == len(runs)
            assert page.locator('#case-judgments h3').count() == 4 * len(runs)
            cid = page.locator('#case-id').input_value()
            source = next((r for r in runs if r['rubric_version']=='source_grounded_v2'), runs[0])
            saved = [r for r in source['scores'] if r['case_id']==cid]
            actual_reasons = page.locator('#case-judgments > details').first.locator('pre').all_text_contents()
            assert actual_reasons == [r['reason'] for r in saved]
        page.locator("#case-scope").select_option("invalid")
        assert page.locator("#case-id option").count() == 5
        page.locator("#case-phase").select_option("phase1")
        assert page.locator('#case-judgments > details').count() == 0
        assert page.locator("#case-id option").count() == 2
        page.locator("#case-scope").select_option("all")
        assert page.locator("#case-id option").count() == 30
        page.locator("#show-train").uncheck()
        assert page.locator("#loss-charts svg").count() == 2
        page.locator("#show-train").check()
        page.locator("#case-phase").select_option("phase2")
        page.locator("#show-greedy").uncheck()
        page.screenshot(path=str(ROOT / "docs/Clinical_Extraction_Phases_desktop.png"), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.screenshot(path=str(ROOT / "docs/Clinical_Extraction_Phases_mobile.png"), full_page=True)
        assert not errors, errors
        assert not external, "The report requested external resources"
        browser.close()
    result = {"browser": "Chrome", "phase_cards": 2, "all_case_outputs": 130,
              "paired_sample_options": 20, "mobile_width": 390,
              "page_errors": errors, "external_requests": len(external)}
    (ROOT / "results_v3/deepeval_20/visualizer_checks.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
