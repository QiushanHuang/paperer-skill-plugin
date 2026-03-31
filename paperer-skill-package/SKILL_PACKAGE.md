# Paperer Skill Package

This directory is the minimal distributable `Paperer` skill package.

## Included Skills

- Public entry skill:
  - `skills/paperer/`
- Thin orchestration skill:
  - `skills/paper-package-runner/`
- Core production skills:
  - `skills/literature-summary/`
  - `skills/paper-asset-extraction/`

## Default Entry Skill

- `skills/paperer/SKILL.md`

Start from that skill first. Do not start from maintainer scripts.

## When To Use This Package

Use this package when:

- the current workspace does not already contain the `Paperer` production skills
- the task is to process a readable paper PDF
- the user does not need the full repo

Do **not** fetch the full repo unless the task is repo-maintainer work or the user explicitly asks for full-repo artifacts.

## Source Directory

- `https://github.com/QiushanHuang/paperer-skill-plugin/tree/main/paperer-skill-package`

## One Way To Fetch Only This Directory

```bash
git clone --filter=blob:none --no-checkout https://github.com/QiushanHuang/paperer-skill-plugin.git
cd paperer-skill-plugin
git sparse-checkout init --cone
git sparse-checkout set paperer-skill-package
git checkout main
```

## Minimal Copyable Prompt

```text
Check whether the current workspace already contains the `Paperer` skills. If not, install the minimal skill package from https://github.com/QiushanHuang/paperer-skill-plugin/tree/main/paperer-skill-package at `paperer-skill-package/`. Use Paperer skill to generate a paper package for the PDF at /absolute/path/to/your-paper.pdf.
```
