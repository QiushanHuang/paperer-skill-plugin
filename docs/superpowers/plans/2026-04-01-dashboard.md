# Paperer Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python script that generates a static HTML dashboard organizing paper reports by date, with sidebar navigation and preview card grid.

**Architecture:** Single Python script scans `output/papers/*/report.json`, groups papers by generation date, and writes one HTML page per day plus an `index.html` redirect. All HTML is self-contained with inline CSS.

**Tech Stack:** Python 3 standard library only (`json`, `pathlib`, `datetime`, `argparse`, `html`)

---

## File Map

| File | Responsibility |
|------|---------------|
| `scripts/build_dashboard.py` | Main script: scan, group, render, write |
| `output/index.html` | Generated: redirect to newest daily page |
| `output/daily/YYYY-MM-DD.html` | Generated: one page per day |

No test files — this is a code-generation script where the output is HTML. Verification is manual (`open output/index.html`).

---

### Task 1: Data Collection — scan and parse report.json files

**Files:**
- Create: `scripts/build_dashboard.py`

- [ ] **Step 1: Create script with argument parsing and paper scanning**

```python
#!/usr/bin/env python3
"""Generate a static HTML dashboard from Paperer paper reports."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build Paperer dashboard")
    p.add_argument(
        "--output-root",
        type=Path,
        default=Path("output"),
        help="Root directory containing papers/ (default: output/)",
    )
    return p.parse_args()


def load_paper(report_path: Path) -> dict | None:
    """Load a single paper's metadata from report.json."""
    try:
        data = json.loads(report_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None

    if data.get("status") == "failed":
        return None

    slug = data.get("paper_slug", report_path.parent.name)
    paper_dir = report_path.parent

    # Title: prefer report.json, fall back to summary.md H1
    title = data.get("paper_title", "")
    if not title:
        summary_path = paper_dir / "summary.md"
        if summary_path.exists():
            for line in summary_path.read_text().splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
    if not title:
        title = slug

    # One-sentence summary: extract from summary.md Section 8.2
    bottom_line = ""
    summary_path = paper_dir / "summary.md"
    if summary_path.exists():
        lines = summary_path.read_text().splitlines()
        # Find last non-empty paragraph
        for i in range(len(lines) - 1, -1, -1):
            stripped = lines[i].strip()
            if stripped and not stripped.startswith("#"):
                bottom_line = stripped
                break

    # Generation date: prefer generated_at field, fall back to mtime
    gen_date = data.get("generated_at", "")
    if gen_date:
        try:
            date_obj = datetime.fromisoformat(gen_date)
        except ValueError:
            date_obj = datetime.fromtimestamp(report_path.stat().st_mtime)
    else:
        date_obj = datetime.fromtimestamp(report_path.stat().st_mtime)

    date_str = date_obj.strftime("%Y-%m-%d")

    # Ratings
    ratings = data.get("ratings", {})

    # Venue / authors
    venue = data.get("venue", "")
    authors = data.get("authors", [])
    affiliations = data.get("affiliations", [])
    paper_date = data.get("date", "")

    # Check summary-report.html exists
    has_report = (paper_dir / "summary-report.html").exists()

    return {
        "slug": slug,
        "title": title,
        "bottom_line": bottom_line,
        "gen_date": date_str,
        "venue": venue,
        "authors": authors,
        "affiliations": affiliations,
        "paper_date": paper_date,
        "ratings": ratings,
        "has_report": has_report,
    }


def scan_papers(output_root: Path) -> list[dict]:
    """Scan all papers and return metadata list."""
    papers = []
    papers_dir = output_root / "papers"
    if not papers_dir.exists():
        return papers
    for report_path in sorted(papers_dir.glob("*/report.json")):
        paper = load_paper(report_path)
        if paper:
            papers.append(paper)
    return papers


def group_by_date(papers: list[dict]) -> dict[str, list[dict]]:
    """Group papers by generation date, sorted newest first."""
    groups: dict[str, list[dict]] = {}
    for p in papers:
        groups.setdefault(p["gen_date"], []).append(p)
    return dict(sorted(groups.items(), reverse=True))
```

- [ ] **Step 2: Test scanning locally**

Run:
```bash
python scripts/build_dashboard.py --output-root output/ 2>&1 || echo "ok - script loads"
```

Add a temporary `main()` to verify scanning works:
```python
def main() -> int:
    args = parse_args()
    papers = scan_papers(args.output_root)
    groups = group_by_date(papers)
    for date, ps in groups.items():
        print(f"{date}: {len(ps)} papers")
        for p in ps:
            print(f"  - {p['title']}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

Expected: prints date groups with paper titles.

- [ ] **Step 3: Commit**

```bash
git add scripts/build_dashboard.py
git commit -m "feat: add dashboard script — data scanning and grouping"
```

---

### Task 2: HTML Rendering — generate daily pages

**Files:**
- Modify: `scripts/build_dashboard.py`

- [ ] **Step 1: Add CSS constant**

Add after the imports:

```python
DASHBOARD_CSS = """\
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg: #f5f5f7;
  --card-bg: #ffffff;
  --border: #e5e7eb;
  --text: #1a1a2e;
  --text-secondary: #4b5563;
  --text-muted: #9ca3af;
  --accent: #2962ff;
  --accent-light: #eef2ff;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, "PingFang SC", "Noto Sans SC", sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
}

.layout {
  display: flex;
  min-height: 100vh;
}

/* Sidebar */
.sidebar {
  flex: 0 0 200px;
  background: var(--card-bg);
  border-right: 1px solid var(--border);
  padding: 24px 16px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-title {
  font-size: 1.2em;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 20px;
}

.sidebar a {
  display: block;
  padding: 6px 10px;
  margin-bottom: 2px;
  border-radius: 6px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.85em;
  transition: background 0.15s;
}

.sidebar a:hover {
  background: var(--bg);
}

.sidebar a.active {
  background: var(--accent);
  color: #fff;
  font-weight: 600;
}

.sidebar .count {
  font-size: 0.8em;
  color: var(--text-muted);
  margin-left: 4px;
}

.sidebar a.active .count {
  color: rgba(255,255,255,0.7);
}

/* Main */
.main {
  flex: 1;
  padding: 32px;
  max-width: 900px;
}

.day-heading {
  font-size: 1.3em;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--accent-light);
}

/* Card grid */
.card-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.paper-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
}

.paper-card .card-title {
  font-size: 0.95em;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 4px;
  line-height: 1.4;
}

.paper-card .card-meta {
  font-size: 0.78em;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.paper-card .card-summary {
  font-size: 0.82em;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 12px;
  flex: 1;
}

.ratings-row {
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
}

.rating-badge {
  flex: 1;
  text-align: center;
  background: var(--accent-light);
  border-radius: 6px;
  padding: 6px 4px;
}

.rating-badge .score {
  font-size: 1.1em;
  font-weight: 700;
  color: var(--accent);
  line-height: 1.2;
}

.rating-badge .dim {
  font-size: 0.65em;
  color: var(--text-secondary);
  margin-top: 1px;
}

.card-link {
  display: inline-block;
  align-self: flex-end;
  font-size: 0.78em;
  font-weight: 600;
  color: #fff;
  background: var(--accent);
  padding: 4px 12px;
  border-radius: 4px;
  text-decoration: none;
  transition: opacity 0.15s;
}

.card-link:hover { opacity: 0.85; }

.no-report {
  font-size: 0.78em;
  color: var(--text-muted);
  align-self: flex-end;
}

/* Responsive */
@media (max-width: 899px) {
  .sidebar {
    position: static;
    height: auto;
    flex: none;
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--border);
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    padding: 12px 16px;
  }
  .sidebar-title { margin-bottom: 0; margin-right: 12px; }
  .layout { flex-direction: column; }
  .card-grid { grid-template-columns: 1fr 1fr; }
  .main { padding: 20px 16px; }
}

@media (max-width: 599px) {
  .card-grid { grid-template-columns: 1fr; }
}
"""
```

- [ ] **Step 2: Add HTML rendering functions**

```python
from html import escape


DIMS = [
    ("novelty", "创新"),
    ("rigor", "严谨"),
    ("practicality", "实用"),
    ("clarity", "清晰"),
    ("impact", "影响"),
]


def render_card(paper: dict) -> str:
    """Render a single paper card."""
    title = escape(paper["title"])
    meta_parts = []
    if paper["affiliations"]:
        meta_parts.append(escape(paper["affiliations"][0]))
    elif paper["authors"]:
        meta_parts.append(escape(paper["authors"][0]) + " et al.")
    if paper["venue"]:
        meta_parts.append(escape(paper["venue"]))
    if paper["paper_date"]:
        meta_parts.append(escape(paper["paper_date"]))
    meta = " · ".join(meta_parts) if meta_parts else ""

    summary = escape(paper["bottom_line"]) if paper["bottom_line"] else ""
    if len(summary) > 120:
        summary = summary[:117] + "..."

    # Ratings
    ratings = paper.get("ratings", {})
    if ratings:
        badges = []
        for key, label in DIMS:
            entry = ratings.get(key, {})
            score = entry.get("score", "—") if isinstance(entry, dict) else "—"
            badges.append(
                f'<div class="rating-badge">'
                f'<div class="score">{score}</div>'
                f'<div class="dim">{label}</div>'
                f'</div>'
            )
        ratings_html = f'<div class="ratings-row">{"".join(badges)}</div>'
    else:
        ratings_html = '<div class="ratings-row" style="color:var(--text-muted);font-size:0.8em;">未评分</div>'

    # Link
    if paper["has_report"]:
        link_html = f'<a class="card-link" href="../papers/{escape(paper["slug"])}/summary-report.html">查看报告 →</a>'
    else:
        link_html = '<span class="no-report">报告生成中...</span>'

    return f"""\
<div class="paper-card">
  <div class="card-title">{title}</div>
  <div class="card-meta">{meta}</div>
  <div class="card-summary">{summary}</div>
  {ratings_html}
  {link_html}
</div>"""


def render_sidebar(groups: dict[str, list[dict]], active_date: str) -> str:
    """Render the sidebar navigation."""
    links = []
    for date, papers in groups.items():
        cls = ' class="active"' if date == active_date else ""
        count = len(papers)
        links.append(
            f'<a href="{date}.html"{cls}>{date}<span class="count">({count}篇)</span></a>'
        )
    return f"""\
<nav class="sidebar">
  <div class="sidebar-title">📚 Paperer Daily</div>
  {"".join(links)}
</nav>"""


def render_daily_page(
    date: str,
    papers: list[dict],
    groups: dict[str, list[dict]],
) -> str:
    """Render a full daily page."""
    sidebar = render_sidebar(groups, date)
    cards = "\n".join(render_card(p) for p in papers)
    count = len(papers)

    return f"""\
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Paperer Daily — {date}</title>
  <style>{DASHBOARD_CSS}</style>
</head>
<body>
  <div class="layout">
    {sidebar}
    <main class="main">
      <h1 class="day-heading">{date} · {count} 篇论文</h1>
      <div class="card-grid">
        {cards}
      </div>
    </main>
  </div>
</body>
</html>"""
```

- [ ] **Step 3: Commit**

```bash
git add scripts/build_dashboard.py
git commit -m "feat: add dashboard HTML rendering — cards, sidebar, daily page"
```

---

### Task 3: File Writing — generate output and index.html

**Files:**
- Modify: `scripts/build_dashboard.py`

- [ ] **Step 1: Replace temporary main() with final version**

Replace the existing `main()` function:

```python
def main() -> int:
    args = parse_args()
    papers = scan_papers(args.output_root)
    if not papers:
        print("[dashboard] No papers found in", args.output_root / "papers")
        return 1

    groups = group_by_date(papers)
    daily_dir = args.output_root / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)

    # Generate daily pages
    for date, day_papers in groups.items():
        html = render_daily_page(date, day_papers, groups)
        out_path = daily_dir / f"{date}.html"
        out_path.write_text(html)
        print(f"[dashboard] Wrote {out_path} ({len(day_papers)} papers)")

    # Generate index.html redirect
    newest_date = next(iter(groups))
    index_html = f"""\
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=daily/{newest_date}.html">
  <title>Paperer Daily</title>
</head>
<body>
  <p>Redirecting to <a href="daily/{newest_date}.html">{newest_date}</a>...</p>
</body>
</html>"""
    index_path = args.output_root / "index.html"
    index_path.write_text(index_html)
    print(f"[dashboard] Wrote {index_path} → daily/{newest_date}.html")

    total = sum(len(ps) for ps in groups.values())
    print(f"[dashboard] Done — {total} papers across {len(groups)} days")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run the script and verify output**

Run:
```bash
python scripts/build_dashboard.py --output-root output/
```

Expected output:
```
[dashboard] Wrote output/daily/2026-04-01.html (2 papers)
[dashboard] Wrote output/index.html → daily/2026-04-01.html
[dashboard] Done — 2 papers across 1 days
```

- [ ] **Step 3: Verify in browser**

Run:
```bash
open output/index.html
```

Expected: redirects to `daily/2026-04-01.html`, shows sidebar with date list and two paper cards with ratings.

- [ ] **Step 4: Verify card links work**

Click "查看报告 →" on each card. Should navigate to `../papers/<slug>/summary-report.html`.

- [ ] **Step 5: Commit**

```bash
git add scripts/build_dashboard.py output/index.html output/daily/
git commit -m "feat: complete dashboard generator — daily pages with index redirect"
```
