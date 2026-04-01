---
name: literature-summary
description: Use when a readable academic paper PDF needs to be turned into a polished literature brief in a user-specified language, especially when figures, tables, and formulas must be explained and missing extraction must be reported explicitly.
---

# Literature Summary

## Overview

Turn a readable paper PDF into a polished research brief.

Core principle: polished partial output is better than confident fabrication.

## When to Use

Use this skill when the user wants a structured literature summary from a readable paper PDF, in a specified language, with visual explanation blocks and explicit handling of missing extraction.

For the fastest fresh-machine and minimal-input entry path, prefer `paper-package-runner` as the wrapper skill and let it call this skill.

Do not use this skill when:

- the input is not a paper PDF
- the PDF is image-only or unreadable and no other extraction skill can recover it
- the user only wants a short abstract-level summary

## Required Inputs

- one readable paper PDF or an explicit `paper_pdf_path`

Optional:

- `target_language`
- `paper_slug`
- `output_root`
- user reading focus

## Standard Intake

- If the paper PDF or `paper_pdf_path` is missing, ask for it before writing.
- If `target_language` is missing, default it to `Chinese`.
- If `paper_slug` is missing, derive it from the PDF filename when possible.
- If `output_root` is missing, default to `output/papers/<paper-slug>/`.
- If user reading focus is missing, continue without it.

If this skill is called from `paper-package-runner`, accept the wrapper's derived defaults unless the user has explicitly requested overrides.

## Workflow

1. Build the evidence bundle.
   Prefer `paper-asset-extraction` as the first visual-asset pipeline. If it is available, use it to gather:
   - `assets/figures/*`
   - `assets/tables/*`
   - `assets/formulas/*`
   - `manifest.json`
   - `extracted/asset-extraction-report.json`

2. If `paper-asset-extraction` is unavailable or fails, fall back to generic PDF-reading and screenshotting skills. If `pdf` is available, use it for extraction and visual checks. Gather:
   - full extracted text
   - metadata when available
   - one header screenshot
   - every detectable figure, table, and formula screenshot
   - explicit extraction issues for any missing or uncertain asset

3. Validate the bundle against [references/bundle-contract.md](references/bundle-contract.md).
   If `manifest.json` is present, use it as the primary visual-asset contract.

4. Read [references/summary-template.md](references/summary-template.md) and write `summary.md`.
   The output must:
   - use the Chinese translation of the paper's English title as the displayed page title, even when the rest of the summary follows another `target_language`
   - follow the selected language
   - read like a professional research brief
   - treat each template bullet as a compact coverage prompt and answer it in polished prose
   - embed the header image and every available figure and table directly in the Markdown
   - explain each figure in full sentences that make clear what it is, what can be observed, and what role it plays in the paper's argument
   - explain each table in full sentences that identify the comparison target, key metrics, notable results, and why they matter
   - **rewrite every formula in LaTeX** (`$$...$$` or `$...$`) rather than embedding formula PNG screenshots — use the PNG crops in `assets/formulas/` only as a visual reference to verify LaTeX accuracy, never as the embedded representation
   - explain each formula in full sentences that identify its role, prioritize core formulas when there are many, and avoid forced interpretation when the paper does not support one
   - keep evidence anchors mainly in technical sections
   - respect asset-level uncertainty from `manifest.json`
   - keep the prose focused on the paper itself rather than the extraction workflow
   - let `1.3 核心结论速览` expand to multiple problem / method / result / contribution points when the paper supports them

5. Apply the failure rules from [references/failure-rules.md](references/failure-rules.md).

6. Write `report.json`.
   Record completeness, missing assets, unreadable regions, explicit errors, and any propagated uncertainty from `paper-asset-extraction`.

7. If this skill is being authored in `paperer-skill-plugin`, follow [references/sync-policy.md](references/sync-policy.md) for mirroring into `Paperer`.

## Quick Reference

- For portable or fresh-machine entry, start with `paper-package-runner`.
- The displayed page title is always the Chinese translation of the paper's English title.
- Aside from that title rule, output language follows `target_language`, which defaults to `Chinese` when omitted.
- Prefer `paper-asset-extraction` for figures, tables, and formulas.
- If `manifest.json` exists, trust its asset paths, types, page numbers, and flags.
- Do not keep Chinese headings when the selected language is not Chinese.
- Do not use ratings; explain judgment in prose.
- Technical sections should include page, figure, table, or equation anchors when available.
- Every figure, table, and formula block must be embedded and explained in complete prose, not labeled QA bullets.
- `summary.md` should not talk about crop choices, screenshot quality, or similar process-side issues.
- Separate the authors' claimed contribution from the paper's supported contribution.
- If extraction is partial, still produce a clean summary and an explicit `report.json`.

## Final Checks

Before finishing, confirm:

- `summary.md` is polished rather than note-like
- section hierarchy is stable
- no placeholders or broken references remain
- every included visual has explanation text
- every included visual is actually embedded in `summary.md`
- missing visuals or unreadable sections are disclosed cleanly
- manifest-level quality flags are reflected in the prose and `report.json`
- extraction-process details stay in `report.json`, not in the main summary prose
- `report.json` matches the actual completeness of the bundle
- `summary.md` uses standard Markdown syntax (headings, images, footnotes, math delimiters) so that the downstream `publish` skill can convert it cleanly into an HTML report

## Common Mistakes

| Mistake | Correction |
|--------|------------|
| Summarizing only the abstract | Read the full available paper text and use the visuals. |
| Ignoring `manifest.json` quality flags | Propagate uncertainty into both explanation strength and `report.json`. |
| Asking the user for `target_language`, `paper_slug`, or `output_root` even when defaults are safe | Default `target_language` to `Chinese`, derive `paper_slug` from the PDF filename, and default the output root unless the user asks to override them. |
| Keeping Chinese headings for every language | Localize the whole report to `target_language` unless the user asks for bilingual output. |
| Dumping screenshots without interpretation | Every visual block needs a short explanation and its role in the argument. |
| Embedding formula PNG screenshots instead of LaTeX | Rewrite formulas as `$$...$$` LaTeX — use PNG crops only as a reference to verify transcription accuracy. |
| Guessing missing method or formula details | Mark uncertainty explicitly and record it in `report.json`. |
| Writing about crop quality or extraction strategy inside the summary | Keep workflow-side issues in `report.json`; keep `summary.md` focused on the paper itself. |
| Letting the displayed page title follow the target language | Always use the Chinese translation of the paper's English title as the displayed page title, and keep the original English title in metadata. |
| Writing a rough note dump | Rewrite into publication-ready prose with stable structure. |
