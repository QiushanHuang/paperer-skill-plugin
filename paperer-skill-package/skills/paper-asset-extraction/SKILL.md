---
name: paper-asset-extraction
description: Use when a readable academic paper PDF needs figure, table, and formula crops organized into a manifest-driven asset bundle, especially when missed content is worse than oversized crops and extraction quality must be flagged explicitly.
---

# Paper Asset Extraction

## Overview

Extract figure, table, and formula assets from a readable paper PDF into a conservative, manifest-driven bundle.

Core principle: missing content is worse than extra margin.

## When to Use

Use this skill when the user wants:

- figures, tables, and formulas extracted from a paper PDF
- a structured `manifest.json` for downstream processing
- conservative crops that prefer completeness over neatness
- explicit quality flags for ambiguous extraction

Do not use this skill when:

- the input is not a readable paper PDF
- the PDF is image-only or otherwise unreadable and no PDF-reading skill can recover it
- the user wants a literature summary rather than the extraction bundle itself

## Required Input

- one readable paper PDF

Optional:

- `paper_slug`
- output root path

## Workflow

1. Build page-level visual context using the available PDF-reading and screenshotting capabilities.
   Prefer the installed `pdf` skill or equivalent tooling to inspect layout, captions, and visible display blocks.

2. Run a two-pass extraction process using [references/extraction-policy.md](references/extraction-policy.md).
   - Pass 1: collect all plausible figure and table candidates, plus only those formula candidates that are standalone displayed equation blocks outside normal paragraph flow and carry an explicit equation cue.
   - Pass 2: review, normalize, deduplicate, verify numbering continuity, split mixed assets, and widen any crop that risks losing content.

3. Write conservative assets into:
   - `assets/figures/`
   - `assets/tables/`
   - `assets/formulas/`

4. Write `manifest.json` using [references/manifest-schema.md](references/manifest-schema.md).

5. Apply [references/quality-flags.md](references/quality-flags.md) to both asset-level and global extraction risks.

6. Write `extracted/asset-extraction-report.json`.

7. Record the repair batch in `logs/fix-logs/` whenever you are correcting extraction defects discovered during testing.

8. If this extraction is being prepared for `literature-summary`, follow [references/integration-contract.md](references/integration-contract.md).

## Quick Reference

- Prefer `oversized_crop` over `tight_crop_risk`.
- Prefer preserving a questionable candidate over silently dropping likely content.
- Figures should keep labels, legends, and panel markers when possible.
- Tables should keep full row/column structure and visible headers.
- Treat as formulas only standalone displayed equation blocks outside body paragraphs, with cues such as `Eq.`, `Equation`, `公式`, or visible equation numbering.
- Do not treat inline math, prose fragments, or symbol-heavy sentences as formulas.
- Formulas should keep the full displayed block and equation number when possible.
- If formula numbering is visible, formula ids must match the paper numbering.
- If a formula number is skipped, re-check the paper before finalizing the bundle.
- Do not crop away any formula line, bracket, operator, or equation label.
- If figure or table numbering is detectable, asset ids must match the paper numbering.
- If a figure number is skipped, re-check the paper before finalizing the bundle.
- One emitted crop should correspond to one labeled figure or one labeled table unless the paper itself presents them as one numbered asset with subpanels.
- Use `partial` when the asset set is probably incomplete.
- Use `failed` only when the bundle is not meaningfully consumable downstream.

## Final Checks

Before finishing, confirm:

- every emitted asset is listed in `manifest.json`
- asset types and page numbers are present
- figure, table, and formula ids match the paper labels when those labels are visible
- numbering is continuous for detected figures and tables, and for numbered formulas unless the gap is explicitly marked as partial
- obvious duplicates are removed or flagged
- mixed figure-table crops are split or explicitly failed for rework
- formula assets are true standalone equation blocks rather than inline paragraph fragments
- likely missing sibling panels or split equations are flagged
- `manifest.json` and `asset-extraction-report.json` agree on status

## Common Mistakes

| Mistake | Correction |
|--------|------------|
| Cropping too tightly for visual cleanliness | Widen the crop and mark `oversized_crop` if needed. |
| Dropping uncertain blocks too early | Keep them and mark `uncertain_type` or another quality flag. |
| Treating multiline equations as separate assets by default | Prefer one logical formula block unless there is strong evidence otherwise. |
| Emitting paragraph math as formulas | Only emit standalone displayed equations with explicit equation cues or numbering. |
| Hiding missed-content risk | Mark `possible_missed_sibling` or a global missing-assets flag explicitly. |
| Emitting assets without a manifest | `manifest.json` is required for downstream use. |
| Letting file ids drift away from the paper numbering | If the paper says `Fig. 7`, the emitted file should be `fig-007.*`. |
| Keeping one crop that contains both a figure and a table | Split them into separate assets and review the numbering again. |
