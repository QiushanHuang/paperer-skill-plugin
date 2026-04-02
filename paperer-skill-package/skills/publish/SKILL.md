---
name: publish
description: Use when a prepared Paperer `summary.md` needs to be converted into the canonical HTML brief and reading pages.
---

# Publish

Use the canonical Paperer renderer scripts. Do not hand-write or improvise the HTML.

## Input

- Required: path to `summary.md`
- Expected sibling files:
  - `report.json`
  - `source.pdf`
  - `assets/`

## Required outputs

When the input file is `summary.md`, write both of these files into the same directory:

- `summary-report.html`
- `summary.html`

## Canonical implementation

Run the fixed renderer script instead of manually building HTML:

```bash
python3 -B scripts/render_summary_report.py path/to/summary.md
```

If the script is not in `scripts/`, resolve it relative to the Paperer plugin root. The canonical helper module is `scripts/paper_summary_utils.py`.

## Hard rules

- `summary-report.html` and `summary.html` must come from the canonical renderer script.
- `summary-report.html` must keep the same structural contract as the 2026-04-01 reference bundles:
  - top-right `header-actions` links to `source.pdf` and `summary.html`
  - right-side `header-shot-wrap` screenshot card
  - `point-row` + `tldr-tag` layout for the brief summary rows
  - `visuals-grid` for key visuals
  - `equation-row` for key equations when applicable
  - `bottomline` closing block
  - clickable glossary terms via `.term` and `data-def`
  - image lightbox via `openImageLightbox`
  - equation lightbox via `openEquationLightbox`
- Ratings must be read only from `report.json`.
- Raw `report.json` rating scores remain on the 1–5 source scale.
- Visible rating display in `summary-report.html` must be normalized to `/10`.
- `summary.html` must omit the ratings section entirely.
- `summary.html` must preserve glossary interaction and image click-to-zoom behavior.
- If formulas are only available as extracted images, keep them inside the canonical equation-card interaction instead of falling back to a separate ad-hoc widget.

## Post-run checklist

- `summary-report.html` exists
- `summary.html` exists
- `summary-report.html` contains:
  - `header-shot-wrap`
  - `AI评分`
  - `/10`
  - `class="term"`
  - `openImageLightbox`
- `summary.html` contains:
  - `class="term"`
  - `openImageLightbox`
  - no visible `AI评分`

## Failure handling

- If rendering fails, surface the error clearly.
- Do not silently replace the canonical template with a simplified fallback.
