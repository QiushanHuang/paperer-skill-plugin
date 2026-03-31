# Bundle Contract

Normalize upstream extraction into a stable paper bundle before writing the final summary.

If `paper-asset-extraction` is available, prefer its `manifest.json` and `extracted/asset-extraction-report.json` as the visual-asset contract.

## Expected bundle

```text
paper-bundle/
  source.pdf
  manifest.json
  extracted/
    fulltext.md
    metadata.json
    errors.json
    asset-extraction-report.json
  assets/
    header/
      paper-header.png
    figures/
      fig-001.png
    tables/
      table-001.png
    formulas/
      formula-001.png
```

## Minimum required for full-quality output

- readable full paper text or a near-complete extraction
- paper title
- authors and affiliations when available
- one header screenshot
- screenshots for every detectable figure
- screenshots for every detectable table
- screenshots for every detectable formula
- `manifest.json` when the paper used `paper-asset-extraction`

## Output artifacts

After writing the summary, the bundle should contain:

```text
paper-bundle/
  source.pdf
  manifest.json
  summary.md
  report.json
  extracted/
  assets/
```

## `report.json` fields

At minimum include:

- `target_language`
- `status`
- `asset_manifest_status`
- `missing_sections`
- `missing_assets`
- `unreadable_regions`
- `notes`
- `errors`

Suggested `status` values:

- `complete`
- `partial`
- `failed`

## Validation checklist

Before writing `summary.md`, verify:

- Is the PDF readable enough to summarize beyond the abstract?
- Is the header screenshot present?
- Are figures, tables, and formulas all represented or explicitly missing?
- Is metadata present and internally consistent?
- Do extraction errors explain any missing content?
- If `manifest.json` exists, do its status and flags match the visible asset set?

If not, downgrade to partial output and make the gaps explicit.

Before finishing the bundle, verify:

- Is the header screenshot embedded in `summary.md`?
- Are all available figures, tables, and formulas embedded in `summary.md`?
- Does each visual block explain, in complete prose, what the asset is, what matters in it, and how it supports the paper's argument?
- Does `summary.md` avoid discussing extraction strategy or crop quality?
