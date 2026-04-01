# Paperer Dashboard Design Spec

## Overview

A static HTML dashboard that organizes Paperer paper reports by generation date, with a sidebar date navigator and preview card grid.

## Problem

As papers accumulate in `output/papers/`, there's no way to browse them by date or get an overview. Users need a management page to see what was generated each day, compare ratings, and jump to individual reports.

## Solution

An independent Python script (`scripts/build_dashboard.py`) that scans `output/papers/*/report.json` and generates static HTML pages — one per day plus an index entry point.

## File Structure

```
output/
  index.html              # Redirects to the most recent daily page
  daily/
    2026-04-01.html       # Full page: sidebar + card grid for that day
    2026-03-31.html
    ...
```

Each `daily/YYYY-MM-DD.html` is a self-contained HTML file (inline CSS, no external dependencies). All daily pages share the same sidebar navigation listing every available date.

## Page Layout

### Sidebar (left, fixed-width ~180px)

- Logo/title: "Paperer Daily"
- Date list, newest first
- Each entry shows: date + paper count
- Active date highlighted
- Each entry is an `<a>` link to the corresponding `daily/YYYY-MM-DD.html`

### Main Content (right)

- Date heading with paper count
- 2-column card grid (1-column on mobile)
- Each card contains:
  - Paper title (Chinese translation from `report.json` or `summary.md` H1)
  - Venue/institution + year
  - One-sentence summary (from `summary.md` Section 8.2 bottom line, or first paragraph)
  - Five-dimension ratings as numbers: 创新性, 严谨性, 实用性, 清晰度, 影响力
  - "查看报告 →" link to `../papers/<slug>/summary-report.html`

### `index.html`

A minimal HTML file that redirects to the most recent daily page:

```html
<meta http-equiv="refresh" content="0; url=daily/YYYY-MM-DD.html">
```

## Data Source

### Input

`output/papers/*/report.json` — each file provides:

| Field | Usage | Fallback |
|-------|-------|----------|
| `paper_slug` | Directory name, link target | Directory name |
| `paper_title` | Card title | Parse from `summary.md` H1 |
| `authors` | Card metadata | Omit |
| `venue` | Card metadata | Omit |
| `date` | Card metadata | Omit |
| `ratings` | Five-dimension scores + justifications | Show "未评分" |
| `status` | Skip if `failed` | Include |

### Date Grouping

Generation date is determined by `report.json` file mtime, truncated to `YYYY-MM-DD`. This groups papers by the day they were processed.

If a `generated_at` field is present in `report.json`, prefer it over mtime.

### One-Sentence Summary

Extracted from `summary.md` by finding the last non-empty paragraph (Section 8.2 一句话总结). If `summary.md` doesn't exist, fall back to `paper_title`.

## Styling

Consistent with `summary-report.html`:

- Same color variables (`--accent: #2962ff`, `--bg: #f5f5f7`, `--card-bg: #ffffff`)
- Same font stack (`-apple-system, "PingFang SC", "Noto Sans SC"`)
- Same card styling (rounded corners, subtle shadow)
- Ratings displayed as inline number badges matching the report's rating card style

## Technical Constraints

- **Python standard library only** — no third-party dependencies (`json`, `os`, `pathlib`, `datetime`)
- **Self-contained HTML** — all CSS inline, no external stylesheets or JS frameworks
- **Graceful degradation** — missing fields in `report.json` produce "—" placeholders, never crash
- **Idempotent** — running the script multiple times produces the same output for the same input

## Responsive Behavior

- Desktop (>=900px): sidebar + 2-column grid
- Tablet (600-899px): sidebar collapses to top bar, 2-column grid
- Mobile (<600px): top bar, 1-column stack

## Out of Scope

- Search, filtering, or sorting functionality
- Paper fetching or scheduling (cron)
- Dynamic features requiring a server
- User authentication
- Integration into the paperer skill pipeline (this is a standalone script)

## Usage

```bash
python scripts/build_dashboard.py
# or
python scripts/build_dashboard.py --output-root output/
```

Run after a batch of papers has been processed. Open `output/index.html` in a browser.
