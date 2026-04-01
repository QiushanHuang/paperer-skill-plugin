# Installing Paperer for OpenCode

## Recommended installation

Clone the repository and run the local installer:

```bash
git clone https://github.com/QiushanHuang/paperer-skill-plugin.git ~/plugins/paperer-skill-plugin
cd ~/plugins/paperer-skill-plugin
./scripts/install-opencode.sh
```

This creates a symlink at:

`~/.config/opencode/skills/paperer-skill-plugin`

It also installs Python and Java dependencies, installs the `docling-fast`
hybrid extras, and pre-downloads the EasyOCR models needed by hybrid mode.

Restart OpenCode after the script finishes.

## Alternative git plugin install

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

If you use this route, still run `scripts/install_deps.sh` once from a local
checkout so Python, Java, and the EasyOCR hybrid model cache are prepared
before the first `docling-fast` extraction.

## Verify

Use OpenCode's `skill` tool to list discovered skills and confirm `paperer` is
available.
