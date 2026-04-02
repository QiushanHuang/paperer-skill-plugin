---
name: paper-package-runner
description: Use when the public `paperer` skill routes into the thin orchestration layer behind normal Paperer paper-package generation.
---

# Paper Package Runner

Keep this skill thin. It orchestrates the existing production skills and fixed scripts; it does not re-implement them.

## Required input

- `paper_pdf_path`

Optional:

- `target_language`
- `paper_slug`
- `output_root`
- `user_reading_focus`

## Defaults

- Default `target_language` to `Chinese`
- Derive `paper_slug` from the PDF filename when missing
- Default output to `output/papers/<paper-slug>/`

## Required production flow

```text
paper-package-runner
  -> literature-summary
     -> paper-asset-extraction
  -> publish via scripts/render_summary_report.py
  -> dashboard rebuild via scripts/build_dashboard.py
```

## Invocation contract

After `literature-summary` completes and `summary.md` exists:

1. Run the canonical publish script:

```bash
python3 -B scripts/render_summary_report.py output/papers/<paper-slug>/summary.md
```

2. This must generate both:
   - `output/papers/<paper-slug>/summary-report.html`
   - `output/papers/<paper-slug>/summary.html`

3. The publish step must follow these rules:
   - `summary-report.html` uses the canonical 0401-style brief structure
   - `summary-report.html` reads ratings only from `report.json`
   - raw `report.json` scores remain 1–5
   - visible `summary-report.html` ratings are normalized to `/10`
   - `summary.html` omits ratings but keeps glossary and image/equation lightbox interactions

4. Rebuild the daily dashboard:

```bash
python3 scripts/build_dashboard.py --output-root output
```

5. The daily dashboard must stay aligned with the brief page:
   - read ratings only from `report.json`
   - display the normalized `/10` values
   - use the fixed dashboard template, not hand-authored HTML

## Return contract

Return:

- output directory
- `summary.md`
- `summary-report.html` when present
- `summary.html` when present
- `report.json`
- `manifest.json` when present
- final status: `complete`, `partial`, or `failed`

## What this skill must not do

- rewrite the summary itself
- replace the canonical renderer with hand-written HTML
- derive ratings from `summary.md`
- let `daily`, `summary-report.html`, and `summary.html` drift onto different rating or template conventions
