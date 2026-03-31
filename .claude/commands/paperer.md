---
description: "Use Paperer to turn a readable paper PDF into a structured paper package"
---

Use the bundled Paperer workflow from `paperer-skill-package/skills/paperer/SKILL.md`.

Treat `paperer` as the public entry.

- Ask only for the missing paper PDF path.
- Default the target language to Chinese unless the user explicitly requests another language.
- Let `paper-package-runner`, `literature-summary`, and `paper-asset-extraction` handle the downstream work.
- Do not start from maintainer scripts or repo overview docs unless the user explicitly asks for repo-maintainer work.

