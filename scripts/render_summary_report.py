from __future__ import annotations

import argparse
from html import escape
from pathlib import Path

from paper_summary_utils import (
    METHOD_KEYWORDS,
    RATING_DIMS,
    RESULT_KEYWORDS,
    BundleSummary,
    TermMarker,
    VisualItem,
    build_meta_badges,
    clean_inline_markdown,
    extract_bullets,
    extract_paragraphs,
    find_section,
    load_bundle_summary,
    parse_image,
    pick_key_visuals,
    pick_visual,
    split_markdown_blocks,
    ten_point_score,
    update_report_json,
)


REPORT_CSS = """* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg: #f5f5f7;
  --card-bg: #ffffff;
  --border: #e5e7eb;
  --text: #1a1a2e;
  --text-secondary: #4b5563;
  --text-muted: #9ca3af;
  --accent: #2962ff;
  --accent-light: #eef2ff;
  --tag-bg: #eef2ff;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, "PingFang SC", "Noto Sans SC", sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
}

.page {
  max-width: 1040px;
  margin: 0 auto;
  padding: 32px 24px;
}

.header {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 24px 28px 20px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  position: relative;
}

.header-content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 248px;
  gap: 20px;
  align-items: start;
}

.header-actions {
  position: absolute;
  top: 20px;
  right: 24px;
  display: flex;
  gap: 8px;
}

.header-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 88px;
  padding: 6px 12px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.8em;
  font-weight: 600;
  transition: all 0.2s ease;
}

.header-action:hover {
  border-color: var(--accent);
  background: var(--accent-light);
  color: var(--accent);
}

.header .title-zh {
  font-size: 1.5em;
  font-weight: 700;
  color: var(--text);
  line-height: 1.3;
  margin-bottom: 4px;
  padding-right: 220px;
}

.header .title-en {
  font-size: 0.82em;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.header .meta {
  font-size: 0.8em;
  color: var(--text-secondary);
  line-height: 1.8;
}

.header .meta .venue {
  display: inline-block;
  background: var(--tag-bg);
  color: var(--accent);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.85em;
  margin-right: 6px;
  margin-bottom: 6px;
}

.header .positioning {
  margin-top: 10px;
  font-size: 0.88em;
  color: var(--text-secondary);
  font-style: italic;
  border-top: 1px solid var(--border);
  padding-top: 10px;
}

.header-shot-wrap {
  margin-top: 12px;
}

.header-shot {
  width: 100%;
  display: block;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: #fff;
  cursor: zoom-in;
}

.header-shot-note {
  margin-top: 6px;
  font-size: 0.72em;
  color: var(--text-muted);
  text-align: center;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}

.card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.card.full { grid-column: 1 / -1; }

.card-label {
  font-size: 0.75em;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: var(--accent);
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 2px solid var(--accent-light);
}

.card p, .card li {
  font-size: 0.88em;
  color: var(--text);
  line-height: 1.6;
  margin-bottom: 5px;
}

.point-row {
  position: relative;
  padding-left: 1.15em;
  margin-bottom: 7px;
  font-size: 0.88em;
  color: var(--text);
  line-height: 1.6;
}

.point-row::before {
  content: "→";
  position: absolute;
  left: 0;
  top: 0;
  color: var(--accent);
  font-weight: 700;
}

.point-text {
  display: inline;
}

.tldr-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding-left: 1.15em;
}

.tldr-row::before {
  top: 2px;
}

.tldr-tag {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 3.4em;
  padding: 1px 8px;
  border: 1px solid var(--accent);
  border-radius: 999px;
  background: var(--accent-light);
  color: var(--accent);
  font-size: 0.82em;
  font-weight: 700;
  line-height: 1.5;
}

.card ul { list-style: none; padding: 0; }

.card ul li {
  padding-left: 1.2em;
  text-indent: -1.2em;
}

.card ul li::before {
  content: "→ ";
  color: var(--accent);
  font-weight: 600;
}

.card strong { color: var(--text); font-weight: 600; }

.card figure {
  margin: 10px 0 4px;
  text-align: center;
}

.card figure img {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
  border-radius: 6px;
  cursor: zoom-in;
}

.card figcaption {
  font-size: 0.72em;
  color: var(--text-muted);
  margin-top: 6px;
}

.visuals-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.visuals-grid figure {
  text-align: center;
  margin: 0;
}

.visuals-grid figure img {
  width: 100%;
  max-height: 160px;
  object-fit: contain;
  border-radius: 6px;
  background: var(--bg);
  padding: 4px;
  cursor: zoom-in;
}

.visuals-grid figcaption {
  font-size: 0.7em;
  color: var(--text-muted);
  margin-top: 4px;
}

.equation-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
  padding: 10px 14px;
  background: var(--bg);
  border-radius: 8px;
  cursor: zoom-in;
}

.equation-row .math-display {
  flex: 1 1 auto;
  margin: 0;
  overflow-x: auto;
  text-align: center;
}

.equation-row .math-display img {
  max-width: 100%;
  max-height: 96px;
  object-fit: contain;
}

.equation-row .eq-note {
  flex: 0 0 220px;
  font-size: 0.78em;
  color: var(--text-secondary);
  line-height: 1.4;
}

.bottomline {
  text-align: center;
  padding: 16px 24px;
  background: linear-gradient(135deg, var(--accent-light), #f0f4ff);
  border: 1px solid #d6e0ff;
  border-radius: 10px;
  font-size: 0.92em;
  font-weight: 500;
  color: var(--text);
  box-shadow: 0 1px 3px rgba(41,98,255,0.08);
}

.rating-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 0.85em;
}

.rating-label {
  flex: 0 0 3.5em;
  font-weight: 600;
  color: var(--text);
}

.rating-score {
  flex: 0 0 auto;
  min-width: 3.9em;
  padding: 1px 8px;
  border-radius: 999px;
  background: var(--accent-light);
  color: var(--accent);
  font-size: 0.8em;
  font-weight: 700;
  text-align: center;
}

.rating-note {
  flex: 1;
  font-size: 0.8em;
  color: var(--text-secondary);
  line-height: 1.4;
}

code {
  font-family: "SF Mono", "Fira Code", monospace;
  font-size: 0.85em;
  background: #f1f1f1;
  padding: 1px 5px;
  border-radius: 3px;
}

.term {
  border-bottom: 1px dashed var(--accent);
  cursor: help;
}

.term-tip {
  position: fixed;
  background: var(--text);
  color: #fff;
  font-size: 12px;
  line-height: 1.6;
  padding: 10px 14px;
  border-radius: 8px;
  width: 260px;
  z-index: 1000;
  box-shadow: 0 4px 16px rgba(0,0,0,0.2);
  animation: tipIn 0.15s ease;
  overflow-wrap: break-word;
  word-wrap: break-word;
  text-indent: 0;
}

.term-tip::before {
  content: "";
  position: absolute;
  top: -5px;
  left: var(--arrow-left, 50%);
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-bottom-color: var(--text);
}

@keyframes tipIn {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}

.lightbox {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0,0,0,0.82);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  cursor: zoom-out;
  animation: lbIn 0.2s ease;
}

.lightbox img {
  max-width: 90vw;
  max-height: 65vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  cursor: default;
}

.lightbox-caption {
  color: #e0e0e0;
  font-size: 0.82em;
  font-weight: 600;
  margin-top: 12px;
  text-align: center;
  max-width: 700px;
}

.lightbox-detail {
  color: #b0b0b0;
  font-size: 0.78em;
  line-height: 1.7;
  margin-top: 8px;
  text-align: center;
  max-width: 700px;
}

.lightbox-close {
  position: absolute;
  top: 16px;
  right: 20px;
  background: none;
  border: none;
  color: #fff;
  font-size: 1.6em;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.15s;
}

.lightbox-close:hover { opacity: 1; }

.lightbox-equation {
  background: #fff;
  border-radius: 10px;
  padding: 28px 36px;
  max-width: 80vw;
  max-height: 65vh;
  overflow-y: auto;
  font-size: 1.4em;
  color: var(--text);
  cursor: default;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  text-align: center;
}

.lightbox-equation .eq-label {
  font-size: 0.55em;
  font-weight: 600;
  color: var(--accent);
  margin-bottom: 8px;
}

@keyframes lbIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

@media (max-width: 899px) {
  .header-content { grid-template-columns: 1fr; }
  .grid { grid-template-columns: 1fr; }
  .visuals-grid { grid-template-columns: 1fr; }
  .equation-row { flex-direction: column; gap: 8px; }
  .equation-row .eq-note { flex: none; text-align: center; }
  .page { padding: 16px; }
  .header .title-zh { padding-right: 0; font-size: 1.3em; }
  .header-actions {
    position: static;
    margin-bottom: 12px;
    justify-content: flex-end;
  }
  .tldr-row {
    display: block;
  }
  .tldr-tag {
    margin-bottom: 4px;
  }
}"""

REPORT_SCRIPT = """  <script>
  (function() {
    var activeTip = null;
    function dismiss() {
      if (activeTip) { activeTip.remove(); activeTip = null; }
    }
    document.addEventListener('click', function(e) {
      var term = e.target.closest('.term');
      if (!term || !term.dataset.def) {
        dismiss();
        return;
      }

      e.stopPropagation();
      if (activeTip && activeTip.dataset.anchor === term.dataset.anchor) {
        dismiss();
        return;
      }
      dismiss();

      var tip = document.createElement('div');
      tip.className = 'term-tip';
      tip.textContent = term.dataset.def;
      tip.dataset.anchor = term.dataset.anchor || term.textContent;
      document.body.appendChild(tip);

      var tr = term.getBoundingClientRect();
      var tipW = 260;
      var left = tr.left + tr.width / 2 - tipW / 2;
      var top = tr.bottom + 8;

      if (left < 8) left = 8;
      if (left + tipW > window.innerWidth - 8) left = window.innerWidth - tipW - 8;

      var arrowLeft = Math.max(16, Math.min(tipW - 16, tr.left + tr.width / 2 - left));
      tip.style.left = left + 'px';
      tip.style.top = top + 'px';
      tip.style.setProperty('--arrow-left', arrowLeft + 'px');

      activeTip = tip;
    });
  })();

  (function() {
    function closeLightbox() {
      var lb = document.querySelector('.lightbox');
      if (lb) lb.remove();
    }

    function openImageLightbox(imgSrc, caption, detail) {
      var lb = document.createElement('div');
      lb.className = 'lightbox';
      lb.innerHTML =
        '<button class="lightbox-close">&times;</button>' +
        '<img src="' + imgSrc + '" alt="">' +
        (caption ? '<div class="lightbox-caption">' + caption + '</div>' : '') +
        (detail ? '<div class="lightbox-detail">' + detail + '</div>' : '');
      lb.addEventListener('click', function(e) {
        if (e.target === lb || e.target.classList.contains('lightbox-close')) lb.remove();
      });
      document.body.appendChild(lb);
    }

    function openEquationLightbox(mathHtml, label, detail) {
      var lb = document.createElement('div');
      lb.className = 'lightbox';
      var eqDiv = document.createElement('div');
      eqDiv.className = 'lightbox-equation';
      eqDiv.innerHTML =
        (label ? '<div class="eq-label">' + label + '</div>' : '') +
        '<div class="math-display">' + mathHtml + '</div>';
      lb.innerHTML = '<button class="lightbox-close">&times;</button>';
      lb.appendChild(eqDiv);
      if (detail) {
        var detailDiv = document.createElement('div');
        detailDiv.className = 'lightbox-detail';
        detailDiv.textContent = detail;
        lb.appendChild(detailDiv);
      }
      lb.addEventListener('click', function(e) {
        if (e.target === lb || e.target.classList.contains('lightbox-close')) lb.remove();
      });
      document.body.appendChild(lb);
      if (typeof renderMathInElement === 'function') {
        renderMathInElement(eqDiv, {
          delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '$', right: '$', display: false}
          ]
        });
      }
    }

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') closeLightbox();
    });

    document.addEventListener('click', function(e) {
      var img = e.target.closest('.card figure img, .visuals-grid img, .header-shot, .doc-image, .doc-header-image');
      if (img) {
        e.stopPropagation();
        var figure = img.closest('figure') || img.closest('.header-shot-wrap') || img.closest('.doc-figure');
        var caption = figure?.querySelector('figcaption, .header-shot-note')?.textContent || '';
        var detail = figure?.dataset.detail || '';
        openImageLightbox(img.src, caption, detail);
        return;
      }

      var eqRow = e.target.closest('.equation-row');
      if (eqRow) {
        e.stopPropagation();
        var mathEl = eqRow.querySelector('.math-display');
        var mathHtml = mathEl ? mathEl.innerHTML : '';
        var label = eqRow.querySelector('.eq-note')?.textContent || '';
        var detail = eqRow.dataset.detail || '';
        openEquationLightbox(mathHtml, label, detail);
        return;
      }
    });
  })();

  </script>"""

READING_CSS = """* { margin: 0; padding: 0; box-sizing: border-box; }

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
  font-size: 15px;
  line-height: 1.75;
  color: var(--text);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
}

.doc-page {
  max-width: 1040px;
  margin: 0 auto;
  padding: 28px 20px 40px;
}

.doc-header, .doc-content {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.doc-header {
  padding: 24px 28px;
  margin-bottom: 16px;
}

.doc-actions {
  display: flex;
  gap: 8px;
  margin-top: 14px;
  flex-wrap: wrap;
}

.doc-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 88px;
  padding: 6px 12px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.82em;
  font-weight: 600;
  transition: all 0.2s ease;
}

.doc-action:hover {
  border-color: var(--accent);
  background: var(--accent-light);
  color: var(--accent);
}

.doc-title {
  font-size: 1.75em;
  font-weight: 700;
  line-height: 1.3;
}

.doc-subtitle {
  margin-top: 6px;
  color: var(--text-muted);
  font-size: 0.92em;
}

.doc-note {
  margin-top: 10px;
  color: var(--text-secondary);
  font-size: 0.88em;
  line-height: 1.6;
}

.doc-header-image {
  width: 100%;
  display: block;
  margin-top: 16px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: #fff;
  cursor: zoom-in;
}

.doc-content {
  padding: 28px 32px 36px;
}

.doc-content h1 {
  font-size: 1.75em;
  margin-bottom: 1rem;
}

.doc-content h2 {
  font-size: 1.28em;
  margin: 2rem 0 0.9rem;
  padding-bottom: 0.35rem;
  border-bottom: 2px solid var(--accent-light);
}

.doc-content h3 {
  font-size: 1.02em;
  margin: 1.35rem 0 0.7rem;
  color: var(--accent);
}

.doc-paragraph {
  margin-bottom: 0.95rem;
  color: var(--text);
}

.doc-list {
  list-style: none;
  padding: 0;
  margin: 0.2rem 0 1rem;
}

.doc-list li {
  position: relative;
  padding-left: 1.2em;
  margin-bottom: 0.55rem;
}

.doc-list li::before {
  content: "→";
  position: absolute;
  left: 0;
  top: 0;
  color: var(--accent);
  font-weight: 700;
}

.doc-figure {
  margin: 1.1rem auto 1.35rem;
  text-align: center;
}

.doc-image {
  max-width: min(100%, 720px);
  max-height: 420px;
  width: auto;
  height: auto;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: #fff;
  cursor: zoom-in;
}

.doc-figure figcaption {
  margin-top: 8px;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.term {
  border-bottom: 1px dashed var(--accent);
  cursor: help;
}

.term-tip {
  position: fixed;
  background: var(--text);
  color: #fff;
  font-size: 12px;
  line-height: 1.6;
  padding: 10px 14px;
  border-radius: 8px;
  width: 260px;
  z-index: 1000;
  box-shadow: 0 4px 16px rgba(0,0,0,0.2);
  animation: tipIn 0.15s ease;
  overflow-wrap: break-word;
}

.term-tip::before {
  content: "";
  position: absolute;
  top: -5px;
  left: var(--arrow-left, 50%);
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-bottom-color: var(--text);
}

@keyframes tipIn {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}

.lightbox {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0,0,0,0.82);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  cursor: zoom-out;
  animation: lbIn 0.2s ease;
}

.lightbox img {
  max-width: 90vw;
  max-height: 72vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  cursor: default;
}

.lightbox-caption {
  color: #e0e0e0;
  font-size: 0.82em;
  font-weight: 600;
  margin-top: 12px;
  text-align: center;
  max-width: 700px;
}

.lightbox-detail {
  color: #b0b0b0;
  font-size: 0.78em;
  line-height: 1.7;
  margin-top: 8px;
  text-align: center;
  max-width: 700px;
}

.lightbox-close {
  position: absolute;
  top: 16px;
  right: 20px;
  background: none;
  border: none;
  color: #fff;
  font-size: 1.6em;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.15s;
}

.lightbox-close:hover { opacity: 1; }

@keyframes lbIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

@media (max-width: 899px) {
  .doc-page { padding: 16px; }
  .doc-content { padding: 22px 20px 30px; }
  .doc-title { font-size: 1.45em; }
}"""


def render_point_rows(items: list[str], marker: TermMarker) -> str:
    rows: list[str] = []
    for item in items:
        if not item.strip():
            continue
        rows.append(f'<div class="point-row"><span class="point-text">{marker.apply(item)}</span></div>')
    return "".join(rows)


def render_tldr_rows(items: list[str], marker: TermMarker) -> str:
    rows: list[str] = []
    for item in items:
        label = "要点"
        text = item
        if "：" in item:
            label, text = item.split("：", 1)
        elif ":" in item:
            label, text = item.split(":", 1)
        rows.append(
            '<div class="point-row tldr-row">'
            f'<span class="tldr-tag">{escape(label.strip())}</span>'
            f'<span class="point-text">{marker.apply(text.strip())}</span>'
            "</div>"
        )
    return "".join(rows)


def render_bullet_list(items: list[str], marker: TermMarker) -> str:
    if not items:
        return ""
    body = "".join(f"<li>{marker.apply(item)}</li>" for item in items if item.strip())
    return f"<ul>{body}</ul>"


def render_visual_figure(visual: VisualItem) -> str:
    return (
        f'<figure data-detail="{escape(visual.detail, quote=True)}">'
        f'<img src="{escape(visual.path)}" alt="{escape(visual.alt)}">'
        f"<figcaption>{escape(visual.detail)}</figcaption>"
        "</figure>"
    )


def render_equation_row(formula: VisualItem) -> str:
    return (
        f'<div class="equation-row" data-detail="{escape(formula.detail, quote=True)}">'
        f'<div class="math-display"><img src="{escape(formula.path)}" alt="{escape(formula.alt)}"></div>'
        f'<div class="eq-note">{escape(formula.title)}</div>'
        "</div>"
    )


def render_rating_rows(ratings: dict) -> str:
    rows: list[str] = []
    for key, label in RATING_DIMS:
        entry = ratings.get(key)
        if not entry:
            continue
        rows.append(
            '<div class="rating-row">'
            f'<span class="rating-label">{escape(label)}</span>'
            f'<span class="rating-score">{escape(ten_point_score(entry.get("score")))}</span>'
            f'<span class="rating-note">{escape(str(entry.get("justification", "")).strip())}</span>'
            "</div>"
        )
    return "".join(rows)


def render_report_html(summary: BundleSummary, report: dict) -> str:
    marker = TermMarker()
    used_visuals: set[str] = set()

    positioning_section = find_section(summary.sections, "1.1")
    why_section = find_section(summary.sections, "1.2")
    tldr_section = find_section(summary.sections, "1.3")
    method_section = find_section(summary.sections, "3.1")
    innovation_section = find_section(summary.sections, "3.2")
    results_section = find_section(summary.sections, "4.2")
    limitations_section = find_section(summary.sections, "7.1")
    questions_section = find_section(summary.sections, "7.2")
    bottom_line_section = find_section(summary.sections, "8.2")

    positioning_paragraphs = extract_bullets(positioning_section.lines) if positioning_section else []
    why_paragraphs = extract_bullets(why_section.lines)[:3] if why_section else []
    tldr_points = extract_bullets(tldr_section.lines)[:4] if tldr_section else []
    method_points = (extract_bullets(method_section.lines)[:2] if method_section else []) + (
        extract_bullets(innovation_section.lines)[:2] if innovation_section else []
    )
    result_points = extract_bullets(results_section.lines)[:4] if results_section else []
    limitation_points = (extract_bullets(limitations_section.lines)[:2] if limitations_section else []) + (
        extract_bullets(questions_section.lines)[:1] if questions_section else []
    )
    bottom_line_candidates = extract_bullets(bottom_line_section.lines) if bottom_line_section else []
    bottom_line = bottom_line_candidates[0] if bottom_line_candidates else ""

    method_visual = pick_visual(summary.visuals, METHOD_KEYWORDS, used_visuals)
    result_visual = pick_visual(summary.visuals, RESULT_KEYWORDS, used_visuals)
    key_visuals = pick_key_visuals(summary.visuals, used_visuals, limit=3)
    key_formulas = summary.formulas[:2]

    badges = "".join(f'<span class="venue">{escape(badge)}</span>' for badge in build_meta_badges(summary.metadata))
    authors_line = ", ".join(summary.metadata.authors)
    if summary.metadata.year:
        authors_line = f"{authors_line} · {summary.metadata.year}" if authors_line else summary.metadata.year
    header_meta = f'<div class="meta">{badges}{escape(authors_line)}</div>' if badges or authors_line else ""

    report_title = escape(summary.metadata.title_zh)
    report_title_en = escape(summary.metadata.title_en)
    positioning = marker.apply(positioning_paragraphs[0]) if positioning_paragraphs else ""
    why_html = render_point_rows(why_paragraphs, marker)
    tldr_html = render_tldr_rows(tldr_points, marker)
    method_html = render_point_rows(method_points, marker)
    results_html = render_bullet_list(result_points, marker)
    limitations_html = render_bullet_list(limitation_points, marker)
    visuals_html = "".join(render_visual_figure(visual) for visual in key_visuals)
    formulas_html = "".join(render_equation_row(formula) for formula in key_formulas)
    ratings_html = render_rating_rows(report.get("ratings", {}))
    bottomline_html = marker.apply(bottom_line)

    method_figure_html = render_visual_figure(method_visual) if method_visual else ""
    result_figure_html = render_visual_figure(result_visual) if result_visual else ""
    visual_card_html = (
        f'<div class="card full" style="margin-bottom: 12px;"><div class="card-label">关键图表</div><div class="visuals-grid">{visuals_html}</div></div>'
        if visuals_html
        else ""
    )
    formula_card_html = (
        f'<div class="card full" style="margin-bottom: 12px;"><div class="card-label">关键公式</div>{formulas_html}</div>'
        if formulas_html
        else ""
    )
    rating_card_html = (
        f'<div class="card full" style="margin-bottom: 12px;"><div class="card-label">AI评分</div>{ratings_html}</div>'
        if ratings_html
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{report_title}</title>
  <meta name="paper-slug" content="{escape(str(report.get('paper_slug', '')), quote=True)}">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
    onload="renderMathInElement(document.body, {{
      delimiters: [
        {{left: '$$', right: '$$', display: true}},
        {{left: '$', right: '$', display: false}}
      ]
    }});"></script>
  <style>
{REPORT_CSS}
  </style>
</head>
<body>
  <div class="page">
    <header class="header">
      <div class="header-actions"><a class="header-action" href="source.pdf" target="_blank" rel="noopener noreferrer">打开 PDF</a><a class="header-action" href="summary.html" target="_blank" rel="noopener noreferrer">阅读 Markdown</a></div>
      <div class="header-content">
        <div>
          <div class="title-zh">{report_title}</div>
          <div class="title-en">{report_title_en}</div>
          {header_meta}
          <div class="positioning">{positioning}</div>
        </div>
        <div>
          <div class="header-shot-wrap" data-detail="论文首页截图，包含标题、作者与期刊元数据。"><img class="header-shot" src="{escape(summary.metadata.header_image)}" alt="paper header"><div class="header-shot-note">首页截图</div></div>
        </div>
      </div>
    </header>

    <div class="grid">
      <div class="card">
        <div class="card-label">速览</div>
        {tldr_html}
      </div>

      <div class="card">
        <div class="card-label">为什么值得关注</div>
        {why_html}
      </div>
    </div>

    <div class="grid">
      <div class="card full">
        <div class="card-label">方法</div>
        {method_html}
        {method_figure_html}
      </div>
    </div>

    <div class="grid">
      <div class="card">
        <div class="card-label">关键结果</div>
        {results_html}
        {result_figure_html}
      </div>

      <div class="card">
        <div class="card-label">局限性</div>
        {limitations_html}
      </div>
    </div>

    {visual_card_html}
    {formula_card_html}
    {rating_card_html}

    <div class="bottomline">
      {bottomline_html}
    </div>
  </div>
{REPORT_SCRIPT}
</body>
</html>
"""


def render_summary_markdown_html(summary: BundleSummary, marker: TermMarker) -> str:
    parts: list[str] = []
    lines = summary.body_lines
    index = 0

    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()
        if not stripped:
            index += 1
            continue

        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            title = clean_inline_markdown(stripped[level:].strip())
            level = min(max(level, 1), 3)
            parts.append(f"<h{level}>{escape(title)}</h{level}>")
            index += 1
            continue

        parsed_image = parse_image(stripped)
        if parsed_image:
            alt, image_path = parsed_image
            detail_lines: list[str] = []
            cursor = index + 1
            while cursor < len(lines):
                next_line = lines[cursor].strip()
                if not next_line:
                    break
                if next_line.startswith("#") or next_line.startswith("- ") or parse_image(next_line):
                    break
                detail_lines.append(next_line)
                cursor += 1
            detail = clean_inline_markdown(" ".join(detail_lines)) or alt
            parts.append(
                '<figure class="doc-figure"'
                f' data-detail="{escape(detail, quote=True)}">'
                f'<img class="doc-image" src="{escape(image_path)}" alt="{escape(alt)}">'
                f"<figcaption>{escape(detail)}</figcaption>"
                "</figure>"
            )
            index = cursor
            continue

        if stripped.startswith("- "):
            items: list[str] = []
            cursor = index
            while cursor < len(lines):
                next_line = lines[cursor].strip()
                if not next_line:
                    break
                if not next_line.startswith("- "):
                    break
                items.append(next_line[2:].strip())
                cursor += 1
            body = "".join(f"<li>{marker.apply(item)}</li>" for item in items)
            parts.append(f'<ul class="doc-list">{body}</ul>')
            index = cursor
            continue

        paragraphs: list[str] = []
        cursor = index
        while cursor < len(lines):
            next_line = lines[cursor].strip()
            if not next_line:
                break
            if next_line.startswith("#") or next_line.startswith("- ") or parse_image(next_line):
                break
            paragraphs.append(next_line)
            cursor += 1
        parts.append("".join(f'<p class="doc-paragraph">{marker.apply(line)}</p>' for line in paragraphs))
        index = cursor

    return "".join(parts)


def render_summary_html(summary: BundleSummary, report: dict) -> str:
    marker = TermMarker()
    body_html = render_summary_markdown_html(summary, marker)
    badges = "".join(f'<span class="venue">{escape(badge)}</span>' for badge in build_meta_badges(summary.metadata))
    authors_line = ", ".join(summary.metadata.authors)
    if summary.metadata.year:
        authors_line = f"{authors_line} · {summary.metadata.year}" if authors_line else summary.metadata.year
    header_note = f"{summary.metadata.venue} · {summary.metadata.date_text}".strip(" ·")

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(summary.metadata.title_zh)} · 阅读版</title>
  <style>
{READING_CSS}
  </style>
</head>
<body>
  <div class="doc-page">
    <section class="doc-header">
      <div class="doc-title">{escape(summary.metadata.title_zh)}</div>
      <div class="doc-subtitle">{escape(summary.metadata.title_en)}</div>
      <div class="doc-note">{badges}{escape(authors_line)}</div>
      <div class="doc-note">{escape(header_note)}</div>
      <div class="doc-actions">
        <a class="doc-action" href="summary-report.html" target="_blank" rel="noopener noreferrer">简报页</a>
        <a class="doc-action" href="source.pdf" target="_blank" rel="noopener noreferrer">打开 PDF</a>
        <a class="doc-action" href="summary.md" target="_blank" rel="noopener noreferrer">原始 Markdown</a>
      </div>
      <div class="doc-figure" data-detail="论文首页截图，包含标题、作者与期刊元数据。">
        <img class="doc-header-image" src="{escape(summary.metadata.header_image)}" alt="paper header">
        <figcaption>首页截图</figcaption>
      </div>
    </section>

    <section class="doc-content">
      {body_html}
    </section>
  </div>
{REPORT_SCRIPT}
</body>
</html>
"""


def regenerate_bundle(bundle_dir: Path) -> None:
    summary = load_bundle_summary(bundle_dir)
    report = update_report_json(bundle_dir, summary)
    (bundle_dir / "summary-report.html").write_text(render_report_html(summary, report), encoding="utf-8")
    (bundle_dir / "summary.html").write_text(render_summary_html(summary, report), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render Paperer summary-report.html and summary.html from summary.md")
    parser.add_argument("summary_paths", nargs="+", help="One or more summary.md paths")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for summary_path in args.summary_paths:
        regenerate_bundle(Path(summary_path).resolve().parent)


if __name__ == "__main__":
    main()
