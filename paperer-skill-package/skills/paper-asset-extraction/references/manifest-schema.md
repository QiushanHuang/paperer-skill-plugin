# Manifest Schema

`manifest.json` is the downstream contract consumed by `literature-summary`.

## Required top-level fields

- `paper_slug`
- `status`
- `policy`
- `summary`
- `assets`
- `global_flags`

## Required top-level structure

```json
{
  "paper_slug": "example-paper",
  "status": "partial",
  "policy": {
    "crop_bias": "prefer-larger-over-missing",
    "dedupe": true,
    "second_pass_review": true
  },
  "summary": {
    "figure_count": 0,
    "table_count": 0,
    "formula_count": 0
  },
  "assets": [],
  "global_flags": []
}
```

## Required per-asset fields

- `id`
- `type`
- `page`
- `path`
- `caption_hint`
- `quality_flags`

When figure, table, or formula numbering is visible in the paper, the numeric suffix of `id` must match that paper numbering.

For formula assets, `caption_hint` should preserve the equation cue whenever possible, such as `Eq. (4)`, `Equation (4)`, or `公式（4）`.

## Per-asset structure

```json
{
  "id": "fig-001",
  "type": "figure",
  "page": 3,
  "path": "assets/figures/fig-001.png",
  "caption_hint": "Fig. 1 regional geology map",
  "quality_flags": []
}
```

## Allowed status values

- `complete`
- `partial`
- `failed`
