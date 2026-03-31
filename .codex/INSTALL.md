# Installing Paperer for Codex

The practical Codex installation path today is native skill discovery.

## Prerequisites

- Git

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/QiushanHuang/paperer-skill-plugin.git ~/plugins/paperer-skill-plugin
   ```

2. Create the skill symlink:

   ```bash
   mkdir -p ~/.agents/skills
   ln -sfn ~/plugins/paperer-skill-plugin/paperer-skill-package/skills ~/.agents/skills/paperer-skill-plugin
   ```

3. Restart Codex.

## Verify

```bash
ls -la ~/.agents/skills/paperer-skill-plugin
```

You should see a symlink pointing to the bundled `paperer-skill-package/skills`
directory.

## Notes

- The repository also ships `.codex-plugin/plugin.json` for plugin-oriented
  packaging metadata.
- The skill source of truth remains `paperer-skill-package/`.

