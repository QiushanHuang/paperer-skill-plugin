# Failure Rules

This skill treats partial success as a valid outcome.

## Non-negotiable rules

- Do not invent unsupported claims.
- Do not silently omit missing evidence.
- Do not make the document look unfinished when output is partial.
- Do not over-explain formulas or visuals that were not extracted clearly.

## Required partial-output behavior

If extraction is incomplete:

- still write `summary.md`
- keep the full section structure where possible
- keep the summary focused on what the paper says and supports
- state missing or unclear evidence in `report.json`
- record the same issue in `report.json`
- propagate `manifest.json` uncertainty when present

## Visual handling rules

If a figure, table, or formula screenshot is missing:

- keep the section heading
- note the missing asset cleanly
- explain only what the surviving evidence supports

If the screenshot exists but interpretation is uncertain:

- lower the specificity of the interpretation
- avoid pretending the visual proves more than it does

If `paper-asset-extraction` marked an asset with flags such as `tight_crop_risk`, `possible_missed_sibling`, or `low_readability`:

- use the asset cautiously
- lower the strength of the explanation
- downgrade the paper-level output to `partial` when the uncertainty materially affects interpretation
- do not turn the summary itself into a discussion of extraction quality

## Formula-specific caution

Formula blocks are high-risk for hallucination.

If a formula cannot be read reliably:

- explain its apparent role only at a high level, if defensible
- otherwise mark it as unreadable
- do not fabricate variable meanings
- keep the workflow-side reason in `report.json`, not in the main summary prose

## Example disclosure language

Examples of acceptable wording:

- "The paper appears to use this equation as the main optimization objective, but the extracted notation is incomplete, so the variable-level interpretation is uncertain."
- "The figure is referenced in the paper, but the extracted screenshot is missing, so this section relies on the surrounding text only."
- "The experimental claim is partially supported by Table 2, but the ablation evidence appears incomplete in the extracted materials."

## Paper-focus rule

Do not use `summary.md` to talk about:

- conservative cropping
- extraction failures
- screenshot cleanliness
- OCR noise
- rendering workflow

Those belong in `report.json` and related extraction metadata. The summary itself should stay centered on the paper's claims, evidence, limits, and implications.
