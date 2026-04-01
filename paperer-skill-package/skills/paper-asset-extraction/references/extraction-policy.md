# Extraction Policy

Use the programmatic pipeline when available, then finish with an agent review pass.

## Pass 0: Programmatic Detection (preferred)

When `scripts/extract_assets.py` is available, run it first:

```
python scripts/extract_assets.py <paper.pdf> --output-root <output_root> --paper-slug <slug>
```

The script uses OpenDataLoader PDF for element detection and pymupdf for cropping. It produces `assets/*`, `manifest.json`, and `extracted/asset-extraction-report.json`.

After the script finishes, skip Pass 1 and go directly to Pass 2 (agent review).

Hybrid mode (`docling-fast`) is **enabled by default** for better formula and complex-table detection. If the `opendataloader-pdf-hybrid` server is not running, the script falls back to local mode automatically. Use `--no-hybrid` to force local-only processing.

If the script is unavailable or fails entirely, fall back to the full agent-driven Pass 1 below.

## Pass 1: Candidate Collection (agent fallback)

Collect all plausible candidates for:

- figures
- tables
- formulas

At this stage:

- prefer over-inclusive crops
- do not reject a candidate only because it includes extra caption text, surrounding whitespace, or nearby body text
- keep possible sibling panels visible when you are unsure whether they are separate assets
- only collect formula candidates when they are standalone displayed equation blocks outside paragraph flow and carry an explicit equation cue such as `Eq.`, `Equation`, `公式`, or a visible equation number
- reject inline math, prose fragments with symbols, and sentence-level variable definitions as formula candidates

## Pass 2: Review And Normalization

When Pass 0 was used, this pass operates on the script's output rather than raw candidates. Focus on verification and correction rather than initial detection.

For every candidate (or every script-produced asset):

- classify as `figure`, `table`, `formula`, or `uncertain`
- merge obvious duplicates
- keep alternates only when they preserve otherwise missing content
- widen crops that look too tight
- flag likely missed siblings or adjacent formula lines
- separate mixed crops that contain multiple labeled assets of different types
- if labels are visible, verify that each emitted figure, table, or numbered formula corresponds to exactly one paper number
- if numbering is not continuous, go back and look for the missing figure, table, or formula before finalizing

## Conservative Ordering Rules

Prefer these outcomes in this order:

1. full content with extra margin
2. questionable but preserved candidate
3. neatly cropped but potentially incomplete candidate

Never choose visual tidiness over content preservation.

## Type-Specific Guidance

### Figures

Keep:

- axes
- legends
- panel labels such as `(a)` and `(b)`
- nearby caption text when needed to disambiguate the figure

Rules:

- one crop should map to one numbered figure
- a multi-panel figure is still one figure if the paper gives it one number
- if the crop contains `Fig. 8` and `Table 1`, split them
- emitted file ids should match the paper numbering when the caption is visible

### Tables

Keep:

- full row and column structure
- headers when visible
- enough surrounding context to avoid clipping edges

Rules:

- one crop should map to one numbered table
- do not merge a table with a neighboring figure just because they share a page
- emitted file ids should match the paper numbering when the caption is visible

### Formulas

Keep:

- the full displayed formula
- equation numbers when present
- neighboring lines when needed for multiline expressions
- enough surrounding margin to preserve the full block and its equation cue without truncation

Rules:

- only treat standalone displayed equation blocks outside paragraph flow as formulas
- require an explicit equation cue such as `Eq.`, `Equation`, `公式`, or visible equation numbering
- do not emit inline math, prose fragments, or sentence-level variable definitions as formulas
- one crop should map to one numbered formula
- a multiline displayed equation with one number is still one formula asset
- emitted file ids should match the paper numbering when the number is visible
- if the crop risks cutting off any line, bracket, operator, or equation label, widen it
- if two distinct numbered equations appear in one crop, split them and review numbering again

If the formula is hard to segment cleanly, prefer one larger standalone block over multiple clipped fragments.

## Numbering Review

Before finalizing a bundle:

- list the detected `Fig. N`, `Table N`, and numbered equation labels in paper order
- check for gaps such as `1, 2, 4`
- if a gap exists, re-open the relevant pages and look for the missing asset
- if the missing asset cannot be recovered, mark the bundle `partial`, record the gap explicitly, and add a matching global flag such as `numbering_gap` or `possible_missing_formulas`
