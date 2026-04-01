---
name: paper-package-runner
description: Use when the public `paperer` skill routes into the thin orchestration layer behind normal Paperer paper-package generation.
---

# Paper Package Runner

## Overview

Use this as the thin orchestration skill behind the public `paperer` entry.

Core principle: ask only for the truly blocking input, default the rest safely, and route the run through the existing production skills instead of duplicating their logic.

If the public `paperer` skill is available, normal callers should start there instead of using this internal runner directly.

## When to Use

Use this skill when:

- the public `paperer` skill has already selected this runner
- the task is to maintain the thin orchestration layer behind the public entry
- a workflow already depends on the internal `paper-package-runner` name

Do not use this skill when:

- the task is repo-maintainer rebuild or regression work
- the user explicitly wants to work from `scripts/rebuild_<slug>_bundle.py`
- the input is not a readable paper PDF

## Required Input

- `paper_pdf_path`

Optional:

- `target_language`
- `paper_slug`
- `output_root`
- `user_reading_focus`

## Fast Preflight

Before asking the user anything beyond the PDF path:

1. Check whether the current environment already has the `Paperer` production skills available:
   - `paperer`
   - `paper-package-runner`
   - `literature-summary`
   - `paper-asset-extraction`
   - `publish`
2. If the skills are already available, do not fetch anything.
3. If the skills are not available, obtain only the minimal `Paperer` skill package directory:
   - GitHub directory:
     - `https://github.com/QiushanHuang/paperer-skill-plugin/tree/main/paperer-skill-package`
   - Expected local path after download:
     - `paperer-skill-package/`
   - Expected public entry skill path:
     - `paperer-skill-package/skills/paperer/SKILL.md`
4. Do not fetch the full repo unless the task is repo-maintainer work or the user explicitly asks for full-repo artifacts.
5. If `paperer` is available, prefer starting there for user-facing runs.
6. Do not send the user into repo-maintainer flows such as:
   - `examples/papers/*`
   - `scripts/rebuild_<slug>_bundle.py`
   - `scripts/validate_paper_bundle.py`

The intended fast path is:

1. ensure the production skills are available
2. collect `paper_pdf_path`
3. default `target_language` to `Chinese` unless the user explicitly asks for another language
4. derive the rest unless the user asks for overrides
5. run the package generation flow

## Intake Rules

- If `paper_pdf_path` is missing, ask for it.
- If `target_language` is missing, default it to `Chinese`.
- If `paper_slug` is missing, derive it from the PDF filename.
- If `output_root` is missing, default to `output/papers/<paper-slug>/`.
- If `user_reading_focus` is missing, continue without it.

Do not ask the user for:

- `target_language` when the user has not requested a different language
- `paper_slug` when it can be derived safely
- `output_root` when the default path is acceptable
- repo-maintainer validation preferences during a normal user run

## Invocation Contract

After preflight and intake:

1. Call `literature-summary` as the main production skill.
2. Require `literature-summary` to prefer `paper-asset-extraction` as the visual-asset pipeline.
3. Let `literature-summary` produce the final paper package under:
   - `output/papers/<paper-slug>/`
4. After `literature-summary` completes successfully and `summary.md` exists, call `publish` on the generated `summary.md` to produce a Distill.pub-style HTML report.
   - Input: `output/papers/<paper-slug>/summary.md`
   - Output: `output/papers/<paper-slug>/summary-report.html`
   - Output: `output/papers/<paper-slug>/summary.html`
   - If `publish` fails or is unavailable, the run still counts as `complete` — the HTML report is a best-effort post-processing step. Record the failure in `report.json`.
5. After publish completes (whether it succeeded or not), rebuild the daily dashboard:
   - Run: `python scripts/build_dashboard.py --output-root <output_root_parent>`
     - `<output_root_parent>` is the parent of `papers/` — typically `output/`.
     - If the script is not found at `scripts/build_dashboard.py`, try the path relative to the skill package root: `../../scripts/build_dashboard.py`.
   - This regenerates `output/daily/*.html` and `output/index.html` so the new paper appears immediately.
   - The daily dashboard must read ratings only from `report.json` so it stays aligned with `summary-report.html`.
   - `summary.html` must omit ratings.
   - If the dashboard rebuild fails, the run still counts as `complete` — dashboard is best-effort. Log a warning but do not fail the run.
6. Return:
   - the output directory path
   - the path to `summary.md`
   - the path to `summary-report.html` when present
   - the path to `report.json`
   - the path to `manifest.json` when present
   - the final status: `complete`, `partial`, or `failed`

## Production Flow

The production flow should be treated as:

```text
paper-package-runner
  -> literature-summary
     -> paper-asset-extraction
  -> publish (summary.md -> summary-report.html)
  -> dashboard rebuild (build_dashboard.py -> daily/*.html + index.html)
  -> output/papers/<paper-slug>/
```

The wrapper must stay thin.

It must not:

- rewrite the summary itself
- extract figures, tables, or formulas itself
- redefine the output schema already owned by `literature-summary`
- re-implement Markdown-to-HTML conversion logic already owned by `publish`

## Quick Reference

- Primary entry skill: `paper-package-runner`
- Public entry skill: `paperer`
- Thin orchestration skill: `paper-package-runner`
- Main brief-writing skill: `literature-summary`
- Preferred visual-asset skill: `paper-asset-extraction`
- HTML report skill: `publish`
- Required user input: `paper_pdf_path`
- Defaulted by the skill: `target_language=Chinese`
- Derived by default: `paper_slug`, `output_root`
- Default output path: `output/papers/<paper-slug>/`
- Preferred install target on a fresh machine: `paperer-skill-package/`
- Built-in return contract: output directory, `summary.md`, `summary-report.html` when present, `report.json`, `manifest.json` when present, and final status

## Common Mistakes

| Mistake | Correction |
|--------|------------|
| Asking the user for every optional field up front | Ask only for `paper_pdf_path`; default `target_language` to `Chinese` and derive the rest unless overrides are needed. |
| Starting normal usage from rebuild scripts | Rebuild scripts are for repo-maintainer testing, not the production entry path. |
| Fetching the full repo just to run the skills | Obtain only `paperer-skill-package/` unless maintainer files are actually needed. |
| Assuming a fresh agent should read README first | Start from `paperer`, not from repo overview docs. |
| Exposing `paper-package-runner` as the first user-facing name | Public callers should say `use Paperer skill`; this runner stays thin behind that entry. |
| Calling `paper-asset-extraction` as the only user-facing step | Use `paper-package-runner` as the entry and let `literature-summary` orchestrate the final package. |
| Re-implementing summary or extraction logic in the wrapper | Keep this skill thin and delegate all core work to the existing production skills. |
