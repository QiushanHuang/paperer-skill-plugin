#!/usr/bin/env python3
"""
Extract figures, tables, and formulas from a paper PDF using OpenDataLoader PDF.

Produces a manifest-driven asset bundle compatible with paperer paper-asset-extraction.
Uses OpenDataLoader for programmatic element detection, then pymupdf for cropping.

Usage:
    python extract_assets.py paper.pdf
    python extract_assets.py paper.pdf --output-root output/papers/my-paper/
    python extract_assets.py paper.pdf --paper-slug my-paper --hybrid docling-fast
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

try:
    import fitz
except ImportError:
    sys.exit("pymupdf is required: pip install pymupdf")

try:
    import opendataloader_pdf
except ImportError:
    sys.exit("opendataloader-pdf is required: pip install opendataloader-pdf")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_DPI = 200
CROP_MARGIN_PT = 10
FORMULA_MARGIN_PT = 6
HEADER_HEIGHT_RATIO = 0.35

MIN_FIGURE_WIDTH_PT = 80
MIN_FIGURE_HEIGHT_PT = 40
CAPTION_MATCH_DIST_PT = 250

FIG_NUMBER_RE = [
    r"Fig(?:ure)?\.?\s*(\d+)",
    r"图\s*(\d+)",
]
TABLE_NUMBER_RE = [
    r"Table\s*(\d+)",
    r"表\s*(\d+)",
]
FORMULA_NUMBER_RE = [
    r"Eq(?:uation)?\.?\s*\(?(\d+)\)?",
    r"公式\s*[（(]?(\d+)[)）]?",
    r"\((\d+)\)\s*$",
]

_CAPTION_START_RE = re.compile(
    r"^(Figure|Fig\.?|Table|Eq(?:uation)?\.?|表|图|公式)\s*\d",
    re.IGNORECASE,
)

# Heuristic for recovering displayed equations misclassified as paragraphs.
_PARA_EQ_NUM_RE = re.compile(r"\((\d+)\)")
_MATH_INDICATOR_RE = re.compile(r"[=∇∑∫√±≤≥≈σηλ]")
_PARA_EQ_MAX_HEIGHT_PT = 50
_PARA_EQ_MAX_CONTENT_LEN = 250
_PARA_EQ_MAX_NUM = 30

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Extract paper assets using OpenDataLoader PDF",
    )
    p.add_argument("pdf_path", type=Path, help="Path to the paper PDF")
    p.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Output directory (default: output/papers/<slug>/)",
    )
    p.add_argument(
        "--paper-slug",
        default=None,
        help="Paper slug (default: derived from PDF filename)",
    )
    p.add_argument(
        "--hybrid",
        default="docling-fast",
        help="Hybrid backend name (default: 'docling-fast'). Requires a running "
        "opendataloader-pdf-hybrid server (opendataloader-pdf-hybrid --port 5002). "
        "Falls back to local mode automatically if the server is unreachable.",
    )
    p.add_argument(
        "--no-hybrid",
        dest="hybrid",
        action="store_const",
        const=None,
        help="Disable hybrid mode and use local processing only.",
    )
    p.add_argument(
        "--dpi",
        type=int,
        default=DEFAULT_DPI,
        help=f"Crop resolution (default: {DEFAULT_DPI})",
    )
    p.add_argument(
        "--margin",
        type=float,
        default=CROP_MARGIN_PT,
        help=f"Extra crop margin in PDF points (default: {CROP_MARGIN_PT})",
    )
    return p.parse_args()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def derive_slug(pdf_path: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "-", pdf_path.stem.lower()).strip("-")


def extract_number(text: str, patterns: list[str]) -> int | None:
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return None


# ---------------------------------------------------------------------------
# OpenDataLoader integration
# ---------------------------------------------------------------------------


def run_opendataloader(
    pdf_path: Path,
    work_dir: Path,
    hybrid: str | None = None,
) -> list[dict]:
    """Run OpenDataLoader PDF and return a flat list of detected elements."""
    kwargs: dict = {
        "input_path": [str(pdf_path)],
        "output_dir": str(work_dir),
        "format": "json",
    }
    if hybrid:
        kwargs["hybrid"] = hybrid

    try:
        opendataloader_pdf.convert(**kwargs)
    except Exception as exc:
        if hybrid:
            print(f"[extract] Hybrid mode ({hybrid}) unavailable: {exc}")
            print("[extract] Falling back to local mode …")
            kwargs.pop("hybrid", None)
            opendataloader_pdf.convert(**kwargs)
        else:
            raise

    json_files = sorted(work_dir.glob("**/*.json"))
    if not json_files:
        sys.exit(f"OpenDataLoader produced no JSON output in {work_dir}")

    with open(json_files[0]) as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("kids", "elements", "content", "items"):
            if key in data and isinstance(data[key], list):
                return data[key]
        if "type" in data:
            return [data]
    sys.exit(f"Unexpected JSON structure in {json_files[0]}")


def _is_significant_image(el: dict) -> bool:
    """Filter out page headers, logos, and tiny decorative elements."""
    bb = el.get("bounding box")
    if not bb:
        return False
    w = bb[2] - bb[0]
    h = bb[3] - bb[1]
    return w >= MIN_FIGURE_WIDTH_PT and h >= MIN_FIGURE_HEIGHT_PT


def _build_caption_index(elements: list[dict]) -> list[dict]:
    """Extract caption-like entries from both caption-type and paragraph-type elements."""
    captions: list[dict] = []
    for el in elements:
        t = el.get("type", "").lower()
        content = el.get("content", "")
        if t == "caption":
            captions.append(el)
        elif t == "paragraph" and _CAPTION_START_RE.match(content):
            captions.append(el)
    return captions


def _is_hidden_formula(el: dict) -> bool:
    """Detect displayed equations misclassified as paragraphs by OpenDataLoader."""
    bb = el.get("bounding box")
    if not bb:
        return False
    h = bb[3] - bb[1]
    content = el.get("content", "")
    if h > _PARA_EQ_MAX_HEIGHT_PT or len(content) > _PARA_EQ_MAX_CONTENT_LEN:
        return False
    m = _PARA_EQ_NUM_RE.search(content)
    if not m or int(m.group(1)) > _PARA_EQ_MAX_NUM:
        return False
    return bool(_MATH_INDICATOR_RE.search(content))


def classify_elements(elements: list[dict]) -> dict[str, list[dict]]:
    captions = _build_caption_index(elements)
    # Collect ids of elements already typed as formula to avoid double-counting
    formula_ids = {el.get("id") for el in elements if el.get("type", "").lower() == "formula"}

    out: dict[str, list[dict]] = {
        "figures": [],
        "tables": [],
        "formulas": [],
        "captions": captions,
    }
    recovered_formula_count = 0
    for el in elements:
        t = el.get("type", "").lower()
        if t in ("picture", "image"):
            if _is_significant_image(el):
                out["figures"].append(el)
        elif t == "table":
            out["tables"].append(el)
        elif t == "formula":
            out["formulas"].append(el)
        elif t == "paragraph" and el.get("id") not in formula_ids:
            if _is_hidden_formula(el):
                out["formulas"].append(el)
                recovered_formula_count += 1

    if recovered_formula_count:
        print(f"[extract] Recovered {recovered_formula_count} formulas from paragraph elements")
    return out


# ---------------------------------------------------------------------------
# PDF cropping via pymupdf
# ---------------------------------------------------------------------------


def _bbox_to_rect(
    bbox: list[float],
    page_height: float,
    page_width: float,
    margin: float,
) -> fitz.Rect:
    """Convert OpenDataLoader [left, bottom, right, top] (PDF coords, origin
    bottom-left) to a pymupdf Rect (origin top-left), adding margin and
    clamping to page bounds."""
    left, bottom, right, top = bbox
    x0 = max(left - margin, 0)
    y0 = max(page_height - top - margin, 0)
    x1 = min(right + margin, page_width)
    y1 = min(page_height - bottom + margin, page_height)
    return fitz.Rect(x0, y0, x1, y1)


def crop_region(
    doc: fitz.Document,
    page_num: int,
    bbox: list[float],
    output_path: Path,
    dpi: int,
    margin: float,
) -> list[str]:
    """Crop a bounding-box region from the PDF. Returns quality flags."""
    flags: list[str] = []
    page = doc[page_num - 1]
    rect = _bbox_to_rect(bbox, page.rect.height, page.rect.width, margin)

    if rect.width < 5 or rect.height < 5:
        flags.append("truncated_visual")
        return flags

    orig_w = bbox[2] - bbox[0]
    orig_h = bbox[3] - bbox[1]
    if margin > 0 and (
        margin / max(orig_w, 1) > 0.12 or margin / max(orig_h, 1) > 0.12
    ):
        flags.append("oversized_crop")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pix = page.get_pixmap(clip=rect, dpi=dpi)
    pix.save(str(output_path))
    return flags


def crop_header(doc: fitz.Document, output_dir: Path, dpi: int) -> None:
    page = doc[0]
    r = page.rect
    header_rect = fitz.Rect(
        r.x0, r.y0, r.x1, r.y0 + r.height * HEADER_HEIGHT_RATIO,
    )
    out = output_dir / "assets" / "header"
    out.mkdir(parents=True, exist_ok=True)
    pix = page.get_pixmap(clip=header_rect, dpi=dpi)
    pix.save(str(out / "paper-header.png"))


# ---------------------------------------------------------------------------
# Caption matching
# ---------------------------------------------------------------------------


def _nearest_caption(
    el: dict,
    captions: list[dict],
    asset_type: str = "",
    max_dist: float = CAPTION_MATCH_DIST_PT,
) -> str:
    """Return the nearest matching caption text on the same page.

    Figures/tables: prefer captions below the asset (standard academic layout).
    Formulas: prefer captions with equation cues on the same page.
    Filters captions by asset type to avoid cross-type matches.
    """
    el_page = el.get("page number", 0)
    el_bbox = el.get("bounding box", [0, 0, 0, 0])
    el_bottom = el_bbox[1]  # lowest PDF-y of the asset

    type_filters: dict[str, list[re.Pattern]] = {
        "figure": [re.compile(r"^Fig(?:ure)?\.?\s*\d", re.I), re.compile(r"^图\s*\d")],
        "table": [re.compile(r"^Table\s*\d", re.I), re.compile(r"^表\s*\d")],
        "formula": [re.compile(r"Eq(?:uation)?\.?\s*\(?\d", re.I), re.compile(r"公式")],
    }
    filters = type_filters.get(asset_type, [])

    best_text = ""
    best_score = max_dist
    for cap in captions:
        if cap.get("page number") != el_page:
            continue
        content = cap.get("content", "")
        if filters and not any(f.search(content) for f in filters):
            continue
        cb = cap.get("bounding box", [0, 0, 0, 0])
        cap_top = cb[3]  # highest PDF-y of the caption
        dist = abs(cap_top - el_bottom)
        # Slight preference for captions below the asset
        if cap_top < el_bottom:
            dist *= 0.8
        if dist < best_score:
            best_score = dist
            best_text = content
    return best_text


# ---------------------------------------------------------------------------
# Asset ID assignment + cropping
# ---------------------------------------------------------------------------

_TYPE_DIR = {"figure": "figures", "table": "tables", "formula": "formulas"}
_TYPE_PREFIX = {"figure": "fig", "table": "table", "formula": "formula"}


def process_asset_type(
    doc: fitz.Document,
    elements: list[dict],
    asset_type: str,
    captions: list[dict],
    number_patterns: list[str],
    output_dir: Path,
    dpi: int,
    margin: float,
) -> list[dict]:
    """Assign paper-matching IDs, crop images, return manifest entries."""
    prefix = _TYPE_PREFIX[asset_type]
    dir_name = _TYPE_DIR[asset_type]
    asset_dir = output_dir / "assets" / dir_name
    asset_dir.mkdir(parents=True, exist_ok=True)

    candidates: list[dict] = []
    for el in elements:
        bbox = el.get("bounding box")
        if not bbox:
            continue
        page = el.get("page number", 1)
        content = el.get("content", "")

        # Try extracting number from element's own content
        num = extract_number(content, number_patterns)
        # Then try matched caption
        caption_text = _nearest_caption(el, captions, asset_type)
        if num is None and caption_text:
            num = extract_number(caption_text, number_patterns)

        hint = caption_text or content
        if len(hint) > 300:
            hint = hint[:297] + "..."

        candidates.append({
            "page": page,
            "bbox": bbox,
            "paper_number": num,
            "caption_hint": hint,
        })

    # Stable sort: by page, then top-of-page first (descending PDF-top coord)
    candidates.sort(key=lambda c: (c["page"], -c["bbox"][3]))

    # Fill in missing numbers sequentially, avoiding collisions
    used = {c["paper_number"] for c in candidates if c["paper_number"] is not None}
    seq = 1
    for c in candidates:
        if c["paper_number"] is None:
            while seq in used:
                seq += 1
            c["paper_number"] = seq
            used.add(seq)
            seq += 1

    entries: list[dict] = []
    for c in candidates:
        n = c["paper_number"]
        filename = f"{prefix}-{n:03d}.png"
        out_path = asset_dir / filename
        rel_path = f"assets/{dir_name}/{filename}"

        flags = crop_region(doc, c["page"], c["bbox"], out_path, dpi, margin)

        entries.append({
            "id": f"{prefix}-{n:03d}",
            "type": asset_type,
            "page": c["page"],
            "path": rel_path,
            "caption_hint": c["caption_hint"],
            "quality_flags": flags,
        })

    return entries


# ---------------------------------------------------------------------------
# Numbering gap detection
# ---------------------------------------------------------------------------


def numbering_gaps(entries: list[dict], asset_type: str) -> list[str]:
    if not entries:
        return []
    nums = sorted(int(e["id"].split("-")[1]) for e in entries)
    for i in range(len(nums) - 1):
        if nums[i + 1] - nums[i] > 1:
            return ["numbering_gap", f"possible_missing_{asset_type}s"]
    return []


# ---------------------------------------------------------------------------
# Manifest + report builders
# ---------------------------------------------------------------------------


def build_manifest(
    slug: str,
    figs: list[dict],
    tables: list[dict],
    formulas: list[dict],
    gflags: list[str],
) -> dict:
    all_assets = figs + formulas + tables
    status = "failed" if not all_assets else ("partial" if gflags else "complete")
    return {
        "paper_slug": slug,
        "status": status,
        "policy": {
            "crop_bias": "prefer-larger-over-missing",
            "dedupe": True,
            "second_pass_review": True,
        },
        "summary": {
            "figure_count": len(figs),
            "table_count": len(tables),
            "formula_count": len(formulas),
        },
        "assets": all_assets,
        "global_flags": sorted(set(gflags)),
    }


def build_report(
    slug: str,
    figs: list[dict],
    tables: list[dict],
    formulas: list[dict],
    gflags: list[str],
    hybrid: str | None,
) -> dict:
    all_assets = figs + tables + formulas
    status = "failed" if not all_assets else ("partial" if gflags else "complete")
    mode = f"hybrid: {hybrid}" if hybrid else "local mode"
    return {
        "paper_slug": slug,
        "status": status,
        "summary": {
            "figure_count": len(figs),
            "table_count": len(tables),
            "formula_count": len(formulas),
        },
        "global_flags": sorted(set(gflags)),
        "notes": [
            f"Programmatic extraction via OpenDataLoader PDF ({mode}).",
            f"Recovered {len(figs)} figures, {len(tables)} tables, "
            f"{len(formulas)} formulas, and one header screenshot.",
            "Crops include conservative margin; marked oversized_crop where applicable.",
        ],
        "errors": [],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    args = parse_args()

    pdf_path = args.pdf_path.resolve()
    if not pdf_path.exists():
        sys.exit(f"PDF not found: {pdf_path}")

    slug = args.paper_slug or derive_slug(pdf_path)
    out = (args.output_root or Path(f"output/papers/{slug}")).resolve()
    out.mkdir(parents=True, exist_ok=True)

    print(f"[extract] PDF:    {pdf_path}")
    print(f"[extract] Slug:   {slug}")
    print(f"[extract] Output: {out}")

    # --- 1. OpenDataLoader detection ---
    print("[extract] Running OpenDataLoader PDF …")
    with tempfile.TemporaryDirectory() as tmp:
        elements = run_opendataloader(pdf_path, Path(tmp), args.hybrid)
    print(f"[extract] Detected {len(elements)} elements total")

    cl = classify_elements(elements)
    print(
        f"[extract] Figures={len(cl['figures'])}  Tables={len(cl['tables'])}  "
        f"Formulas={len(cl['formulas'])}  Captions={len(cl['captions'])}"
    )

    # --- 2. Open PDF for cropping ---
    doc = fitz.open(str(pdf_path))

    # --- 3. Header ---
    print("[extract] Cropping header …")
    crop_header(doc, out, args.dpi)

    # --- 4. Figures ---
    print("[extract] Processing figures …")
    fig_entries = process_asset_type(
        doc, cl["figures"], "figure", cl["captions"],
        FIG_NUMBER_RE, out, args.dpi, args.margin,
    )

    # --- 5. Tables ---
    print("[extract] Processing tables …")
    table_entries = process_asset_type(
        doc, cl["tables"], "table", cl["captions"],
        TABLE_NUMBER_RE, out, args.dpi, args.margin,
    )

    # --- 6. Formulas ---
    print("[extract] Processing formulas …")
    formula_margin = min(args.margin, FORMULA_MARGIN_PT)
    formula_entries = process_asset_type(
        doc, cl["formulas"], "formula", cl["captions"],
        FORMULA_NUMBER_RE, out, args.dpi, formula_margin,
    )

    doc.close()

    # --- 7. Global flags ---
    gflags: list[str] = []
    gflags.extend(numbering_gaps(fig_entries, "figure"))
    gflags.extend(numbering_gaps(table_entries, "table"))
    gflags.extend(numbering_gaps(formula_entries, "formula"))

    if not cl["formulas"]:
        gflags.append("possible_missing_formulas")
        if not args.hybrid:
            print(
                "[extract] Warning: no formulas detected in local mode. "
                "Re-run without --no-hybrid for better formula extraction."
            )
        else:
            print("[extract] Warning: no formulas detected even in hybrid mode.")

    # --- 8. Write manifest.json ---
    manifest = build_manifest(slug, fig_entries, table_entries, formula_entries, gflags)
    mpath = out / "manifest.json"
    mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"[extract] Wrote {mpath}")

    # --- 9. Write extraction report ---
    report = build_report(
        slug, fig_entries, table_entries, formula_entries, gflags, args.hybrid,
    )
    edir = out / "extracted"
    edir.mkdir(parents=True, exist_ok=True)
    rpath = edir / "asset-extraction-report.json"
    rpath.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(f"[extract] Wrote {rpath}")

    # --- Summary ---
    print(f"\n[extract] Done — status: {manifest['status']}")
    print(f"  Figures:  {len(fig_entries)}")
    print(f"  Tables:   {len(table_entries)}")
    print(f"  Formulas: {len(formula_entries)}")
    if gflags:
        print(f"  Flags:    {sorted(set(gflags))}")

    return 0 if manifest["status"] != "failed" else 1


if __name__ == "__main__":
    sys.exit(main())
