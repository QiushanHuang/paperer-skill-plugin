---
name: publish
description: "Convert a prepared Markdown file (from academic paper extraction) into a Distill.pub-style HTML report. Use when the user wants to generate an HTML report from a Markdown file, e.g. /publish path/to/paper.md"
---

# Publish

Generate a Distill.pub-style HTML report from a prepared Markdown file.

## Input

The user provides a path to a Markdown file as the argument. The Markdown was extracted from an academic paper (via MinerU) and may have been rewritten upstream with a specific detail level and language.

Read the file using the Read tool. Note the directory path — the output HTML will be written to the same directory.

## Output

Write a single self-contained HTML file to the same directory as the input. The output filename is derived from the input: `<input-name>-report.html` (e.g., `paper.md` → `paper-report.html`).

## Instructions

1. Read the Markdown file provided as the argument
2. Determine the output path: same directory, filename = `<input-basename-without-extension>-report.html`
3. Generate a complete HTML file following the Distill Style Guide and Conversion Rules below
4. Write the HTML file using the Write tool
5. Tell the user the output path and offer to open it

## Distill Style Guide

The HTML report must follow these design principles from Distill.pub:

### Page Layout
- Body content max-width: 700px, centered horizontally
- Full page width available for figures that need to "break out"
- Generous whitespace: padding 60px top, 40px sides minimum
- Right margin reserved for sidenotes (width ~250px) on screens > 1100px

### Typography
- Headings: system sans-serif stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`)
- Body text: serif stack (`Georgia, "Times New Roman", serif`), 18px, line-height 1.8
- Heading sizes: h1 = 2.2em, h2 = 1.6em, h3 = 1.3em
- Text color: `#333` for body, `#111` for headings
- Links: `#2962ff`, no underline, underline on hover

### Meta Header
- Paper title as h1 at the top
- Authors and date below the title in muted style (`#666`, smaller font)
- A thin bottom border separating the header from content

### Table of Contents
- Generated from h2/h3 headings in the Markdown
- Displayed after the meta header as a styled list
- Each entry is an anchor link to the corresponding section
- Styled: `#666` text, no bullets, indented for h3

### Sidenotes
- Convert Markdown footnotes (`[^1]` / `[^1]: text`) into sidenotes
- On wide screens (>1100px): float in the right margin, aligned with the reference point
- On narrow screens: display inline as styled callout blocks with a left border accent
- Sidenote number styled as superscript in `#2962ff`
- Sidenote text in smaller font (14px), `#666` color

### Figures
- Images get a figure container: `<figure>` with `<img>` and `<figcaption>`
- If the Markdown image has alt text, use it as the caption
- Figures can optionally break out to wider width (max 900px) for large images
- Centered, with margin above and below (2em)
- Caption: centered, italic, `#666`, smaller font

### Math (KaTeX)
- Include KaTeX CSS and JS from CDN in the `<head>`
- Inline math: `$...$` in Markdown → `<span class="math-inline">...</span>`, rendered by KaTeX auto-render
- Block math: `$$...$$` in Markdown → `<div class="math-display">...</div>`, rendered by KaTeX auto-render
- Use KaTeX auto-render extension with delimiters for `$...$` and `$$...$$`

### Code Blocks
- Background: `#f6f8fa`, border-radius 6px, padding 16px
- Font: `"SF Mono", "Fira Code", monospace`, 14px
- Overflow-x: auto for long lines
- No syntax highlighting library needed — plain styled `<pre><code>`

### Responsive Design
- Breakpoint at 1100px: sidenotes move from margin to inline
- Breakpoint at 768px: reduce body padding, font sizes scale down slightly
- Images scale to fit viewport width

## Conversion Rules

When converting the Markdown content to HTML, follow these rules:

1. **First h1** → paper title in the meta header. Do not repeat it in the body.
2. **Metadata block** (if present as YAML frontmatter or initial lines with authors/date) → extract into meta header.
3. **Headings** → `<h2>`, `<h3>`, etc. with `id` attributes for TOC anchor links. Generate a TOC from these.
4. **Paragraphs** → `<p>` tags within `<article>` container.
5. **Images** (`![alt](path)`) → `<figure><img src="path" alt="alt"><figcaption>alt</figcaption></figure>`. Preserve the relative path exactly.
6. **Footnotes** (`[^N]` references and `[^N]: definition` blocks) → sidenotes. Place a `<sup class="sidenote-ref">N</sup>` at the reference point. Place the sidenote content in a `<span class="sidenote"><sup>N</sup> text</span>` as a sibling right after the paragraph. Wrap each paragraph that contains footnote refs in a `<div style="position: relative;">` so that absolute-positioned sidenotes align correctly on wide screens.
7. **Inline math** (`$...$`) → keep the delimiters, KaTeX auto-render will process them.
8. **Block math** (`$$...$$`) → wrap `$$...$$` (including the delimiters) in a `<div class="math-display">` for styling; KaTeX auto-render will find and replace the delimiters within.
9. **Code blocks** → `<pre><code>` with appropriate styling.
10. **Bold/italic/lists/tables** → standard HTML equivalents.
11. **Links** → `<a>` tags, open in new tab (`target="_blank"`).

## CSS Template

Embed the following CSS in a `<style>` tag in the HTML `<head>`:

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 18px;
  line-height: 1.8;
  color: #333;
  background: #fff;
}

.container {
  max-width: 700px;
  margin: 0 auto;
  padding: 60px 40px;
  position: relative;
}

/* Meta Header */
.meta-header {
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.meta-header h1 {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 2.2em;
  font-weight: 700;
  color: #111;
  line-height: 1.3;
  margin-bottom: 12px;
}

.meta-header .authors {
  font-size: 0.95em;
  color: #666;
  margin-bottom: 4px;
}

.meta-header .date {
  font-size: 0.85em;
  color: #999;
}

/* Table of Contents */
.toc {
  margin-bottom: 40px;
  padding: 20px 0;
}

.toc h2 {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 1em;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #999;
  margin-bottom: 12px;
}

.toc ul {
  list-style: none;
  padding: 0;
}

.toc li {
  margin-bottom: 6px;
}

.toc li.toc-h3 {
  padding-left: 20px;
}

.toc a {
  color: #666;
  text-decoration: none;
  font-size: 0.95em;
}

.toc a:hover {
  color: #2962ff;
}

/* Headings */
h2, h3, h4 {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: #111;
  margin-top: 2em;
  margin-bottom: 0.5em;
}

h2 { font-size: 1.6em; }
h3 { font-size: 1.3em; }
h4 { font-size: 1.1em; }

/* Body content */
article p {
  margin-bottom: 1.2em;
}

article a {
  color: #2962ff;
  text-decoration: none;
}

article a:hover {
  text-decoration: underline;
}

/* Figures */
figure {
  max-width: 900px;
  margin: 2em auto;
  text-align: center;
}

figure img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

figcaption {
  font-size: 0.85em;
  color: #666;
  font-style: italic;
  margin-top: 8px;
}

/* Sidenotes */
.sidenote-ref {
  font-size: 0.75em;
  vertical-align: super;
  color: #2962ff;
  cursor: pointer;
  font-weight: 600;
}

.sidenote {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 8px;
}

/* Wide screen: sidenotes in margin */
@media (min-width: 1100px) {
  .container {
    max-width: 700px;
    margin-left: auto;
    margin-right: calc(50% - 350px + 140px);
  }

  .sidenote {
    position: absolute;
    right: -280px;
    width: 250px;
  }
}

/* Narrow screen: sidenotes inline */
@media (max-width: 1099px) {
  .sidenote {
    display: block;
    background: #f9f9f9;
    padding: 8px 12px;
    border-left: 3px solid #2962ff;
    margin: 8px 0;
    border-radius: 0 4px 4px 0;
  }
}

/* Code blocks */
pre {
  background: #f6f8fa;
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
  margin-bottom: 1.5em;
}

code {
  font-family: "SF Mono", "Fira Code", "Consolas", monospace;
  font-size: 14px;
}

p code {
  background: #f6f8fa;
  padding: 2px 6px;
  border-radius: 3px;
}

/* Math */
.math-display {
  overflow-x: auto;
  margin: 1.5em 0;
  text-align: center;
}

/* Tables */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5em 0;
}

th, td {
  padding: 10px 14px;
  border-bottom: 1px solid #e0e0e0;
  text-align: left;
}

th {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-weight: 600;
  color: #111;
}

/* Lists */
ul, ol {
  margin-bottom: 1.2em;
  padding-left: 1.5em;
}

li {
  margin-bottom: 0.4em;
}

/* Blockquotes */
blockquote {
  border-left: 3px solid #e0e0e0;
  padding-left: 16px;
  color: #666;
  margin: 1.5em 0;
  font-style: italic;
}

/* Responsive */
@media (max-width: 768px) {
  .container {
    padding: 30px 20px;
  }

  body {
    font-size: 16px;
  }

  .meta-header h1 {
    font-size: 1.8em;
  }

  figure {
    max-width: 100%;
  }
}
```

## HTML Template Structure

Generate the HTML following this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{PAPER_TITLE}}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
    onload="renderMathInElement(document.body, {
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false}
      ]
    });"></script>
  <style>
    /* ... full CSS from above ... */
  </style>
</head>
<body>
  <div class="container">
    <header class="meta-header">
      <h1>{{PAPER_TITLE}}</h1>
      <div class="authors">{{AUTHORS}}</div>
      <div class="date">{{DATE}}</div>
    </header>
    <nav class="toc">
      <h2>Contents</h2>
      <ul>
        <!-- generated from headings -->
      </ul>
    </nav>
    <article>
      <!-- converted Markdown content -->
    </article>
  </div>
</body>
</html>
```

## Long Document Handling

If the Markdown content is very long (you estimate it may push context limits):

1. Read the full Markdown to get the structure (headings, sections)
2. Generate the HTML `<head>` with full CSS and the meta header + TOC first
3. Process the body section by section, appending to the HTML
4. Close the HTML tags at the end
5. Write the complete concatenated result
