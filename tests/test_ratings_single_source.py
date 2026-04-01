import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_DASHBOARD_PATH = REPO_ROOT / "scripts" / "build_dashboard.py"
LITERATURE_SKILL_PATH = (
    REPO_ROOT / "paperer-skill-package" / "skills" / "literature-summary" / "SKILL.md"
)
SUMMARY_TEMPLATE_PATH = (
    REPO_ROOT
    / "paperer-skill-package"
    / "skills"
    / "literature-summary"
    / "references"
    / "summary-template.md"
)
PUBLISH_SKILL_PATH = REPO_ROOT / "paperer-skill-package" / "skills" / "publish" / "SKILL.md"
RUNNER_SKILL_PATH = (
    REPO_ROOT / "paperer-skill-package" / "skills" / "paper-package-runner" / "SKILL.md"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class DashboardRatingsTests(unittest.TestCase):
    def test_daily_renders_ai_scores_in_ten_point_scale_from_report_json(self) -> None:
        dashboard = load_module("build_dashboard", BUILD_DASHBOARD_PATH)

        with tempfile.TemporaryDirectory() as tmpdir:
            paper_dir = Path(tmpdir) / "papers" / "demo-paper"
            paper_dir.mkdir(parents=True)
            (paper_dir / "report.json").write_text(
                json.dumps(
                    {
                        "paper_slug": "demo-paper",
                        "paper_title": "示例论文",
                        "generated_at": "2026-04-02T12:00:00+08:00",
                        "ratings": {
                            "novelty": {"score": 4},
                            "rigor": {"score": 5},
                            "practicality": {"score": 3},
                            "clarity": {"score": 4},
                            "impact": {"score": 4},
                        },
                    },
                    ensure_ascii=False,
                )
            )
            (paper_dir / "summary.md").write_text("# 示例论文\n\n一句话总结。\n")
            (paper_dir / "summary-report.html").write_text("<html></html>")

            paper = dashboard.load_paper(paper_dir / "report.json")
            html = dashboard.render_card(paper)

        self.assertIn("AI评分", html)
        self.assertIn(">8/10<", html)
        self.assertIn(">10/10<", html)
        self.assertNotIn('class="score">4<', html)


class RatingsContractTests(unittest.TestCase):
    def test_summary_markdown_contract_no_longer_requires_inline_rating_table(self) -> None:
        literature_skill = LITERATURE_SKILL_PATH.read_text(encoding="utf-8")
        summary_template = SUMMARY_TEMPLATE_PATH.read_text(encoding="utf-8")

        self.assertNotIn("Include the AI ratings table (Section 9) at the end of `summary.md`", literature_skill)
        self.assertNotIn("`summary.md` includes the AI ratings table", literature_skill)
        self.assertNotIn("### 9. AI 评分", summary_template)
        self.assertIn("`report.json`", summary_template)
        self.assertIn("ratings", summary_template)

    def test_publish_and_runner_document_single_rating_source(self) -> None:
        publish_skill = PUBLISH_SKILL_PATH.read_text(encoding="utf-8")
        runner_skill = RUNNER_SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("summary-report.html", publish_skill)
        self.assertIn("summary.html", publish_skill)
        self.assertIn("summary-report.html", publish_skill)
        self.assertIn("must render ratings only from `report.json`", publish_skill)
        self.assertIn("summary.html", publish_skill)
        self.assertIn("must not display a ratings section", publish_skill)
        self.assertIn("daily dashboard must read ratings only from `report.json`", runner_skill)
        self.assertIn("must omit ratings", runner_skill)


if __name__ == "__main__":
    unittest.main()
