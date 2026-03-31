---
name: paperer
description: Use when the user refers to the Paperer skill by name or wants the shortest public entry for generating a paper package from a readable paper PDF.
---

# Paperer

This is the public Paperer entry skill for normal user-facing paper-package generation.

Start here when the user says "use Paperer skill". Do not start from maintainer scripts or repo overview docs.

## Fast Preflight

1. Check whether the current workspace already contains these Paperer skills:
   - `paperer`
   - `paper-package-runner`
   - `literature-summary`
   - `paper-asset-extraction`
2. If they are already available, fetch nothing.
3. If they are not available, install only the minimal skill package from:
   - `https://github.com/QiushanHuang/paperer-skill-plugin/tree/main/paperer-skill-package`
4. Expected local path after install:
   - `paperer-skill-package/`
5. Expected public entry skill path after install:
   - `paperer-skill-package/skills/paperer/SKILL.md`
6. Do not fetch the full repo unless the task is repo-maintainer work or the user explicitly asks for full-repo artifacts.
7. Do not send normal users into:
   - `scripts/rebuild_*.py`
   - `scripts/validate_paper_bundle.py`
   - repo example-output rebuild flows

## Required Input

- `paper_pdf_path`

Optional:

- `target_language`
- `paper_slug`
- `output_root`
- `user_reading_focus`

## Intake Rules

- Ask only for `paper_pdf_path` when it is missing.
- Default `target_language` to `Chinese` unless the user explicitly requests another language.
- Derive `paper_slug` from the PDF filename when the user does not provide one.
- Default `output_root` to `output/papers/<paper-slug>/`.
- Continue without `user_reading_focus` when it is not provided.

## Invocation Contract

1. Use `paper-package-runner` as the thin orchestration skill behind this public entry.
2. Let `paper-package-runner` route the run to `literature-summary`.
3. Require `literature-summary` to prefer `paper-asset-extraction` as the visual-asset pipeline.
4. Return:
   - the output directory path
   - the path to `summary.md`
   - the path to `report.json`
   - the path to `manifest.json` when present
   - the final status: `complete`, `partial`, or `failed`

## Production Flow

```text
paperer
  -> paper-package-runner
     -> literature-summary
        -> paper-asset-extraction
  -> output/papers/<paper-slug>/
```

## Common Mistakes

| Mistake | Correction |
|--------|------------|
| Fetching the full repo for a normal paper run | Install only `paperer-skill-package/` unless maintainer files are explicitly needed. |
| Making the user name an internal skill | Public callers should say `use Paperer skill`; this skill routes into the internal runner. |
| Starting from repo README or rebuild scripts | Start from `paperer`, not from maintainer docs or rebuild flows. |
