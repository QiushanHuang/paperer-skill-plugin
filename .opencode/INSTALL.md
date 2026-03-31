# Installing Paperer for OpenCode

## Recommended installation

Add the Paperer plugin to the `plugin` array in your `opencode.json`:

```json
{
  "plugin": [
    "paperer-skill-plugin@git+https://github.com/QiushanHuang/paperer-skill-plugin.git"
  ]
}
```

Restart OpenCode after saving `opencode.json`.

The bundled OpenCode plugin auto-registers:

`paperer-skill-package/skills`

## Alternative local install

Run:

```bash
./scripts/install-opencode.sh
```

This creates a symlink at:

`~/.config/opencode/skills/paperer-skill-plugin`

## Verify

Use OpenCode's `skill` tool to list discovered skills and confirm `paperer` is
available.

