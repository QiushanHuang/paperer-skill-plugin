# Quality Flags

Use quality flags to make extraction uncertainty explicit instead of hiding it.

## Per-asset flags

- `oversized_crop`
- `tight_crop_risk`
- `possible_duplicate`
- `possible_missed_sibling`
- `uncertain_type`
- `low_readability`
- `mixed_assets_risk`
- `truncated_visual`

## Global flags

- `possible_missing_figures`
- `possible_missing_tables`
- `possible_missing_formulas`
- `page_layout_ambiguous`
- `asset_set_incomplete`
- `numbering_gap`

## Interpretation rules

- `oversized_crop`
  - acceptable for downstream use; usually does not require severe downgrade
- `tight_crop_risk`
  - high-risk flag; downstream skill should interpret cautiously
- `possible_duplicate`
  - indicates normalization uncertainty
- `possible_missed_sibling`
  - indicates likely incompleteness near the current asset
- `uncertain_type`
  - do not use the asset for strong claims
- `low_readability`
  - use only high-level interpretation
- `mixed_assets_risk`
  - the crop may still contain more than one labeled asset and should be split or reviewed
- `truncated_visual`
  - the crop likely cuts off meaningful visual content and should not be trusted as a final asset

## Status guidance

Typical `partial` triggers:

- one or more major assets likely missing
- important formulas unreadable or fragmented
- one or more numbered formulas are missing from the recovered sequence
- several assets carry `tight_crop_risk`
- one or more figure or table numbers are missing from the recovered sequence
- the overall set appears incomplete
