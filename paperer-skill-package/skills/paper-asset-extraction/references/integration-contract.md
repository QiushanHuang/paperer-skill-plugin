# Integration Contract

`literature-summary` should treat `paper-asset-extraction` as the preferred asset pipeline.

## What the main skill may trust

- asset paths
- asset types
- page numbers
- caption hints
- quality flags
- global extraction warnings

## What the main skill must not assume

- that every asset is clean enough for strong interpretation
- that `complete` means every crop is visually perfect
- that missing warnings can be ignored in the final `report.json`

## Propagation guidance

- consume `manifest.json`
- consume `extracted/asset-extraction-report.json`
- propagate extraction uncertainty into the final literature-summary `report.json`
- downgrade the paper-level status to `partial` when extraction uncertainty materially affects interpretation
