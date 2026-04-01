# Installing Paperer for Codex

The practical Codex installation path today is native skill discovery.

## Prerequisites

- Git
- Python 3.10+
- Java 11+ (required by opendataloader-pdf at runtime)

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

3. Install Python dependencies and Java (runs once, idempotent):

   ```bash
   bash ~/plugins/paperer-skill-plugin/scripts/install_deps.sh
   ```

4. Enable hooks in Codex (for automatic dependency detection on session start):

   Add this to `~/.codex/config.toml`:

   ```toml
   [features]
   codex_hooks = true
   ```

   Then copy the hooks config to the Codex hooks location:

   ```bash
   mkdir -p ~/.codex
   cp ~/plugins/paperer-skill-plugin/hooks/codex-hooks.json ~/.codex/hooks.json
   ```

   Or merge with your existing `~/.codex/hooks.json` if you already have hooks.

5. Restart Codex.

## Verify

```bash
ls -la ~/.agents/skills/paperer-skill-plugin
```

You should see a symlink pointing to the bundled `paperer-skill-package/skills`
directory.

## What the hook does

On each session start, the `SessionStart` hook:

- Detects whether Python, Java, and extraction dependencies are available
- Silently installs missing Python packages into a project-local `.venv` if needed
- Reports the pipeline status (`ready`, `degraded`, or `unavailable`) to the agent

If the hook is not enabled, the skills still work — they include a Dependency
Preflight section that performs the same checks at runtime.

## Notes

- The repository ships `.codex-plugin/plugin.json` with a `hooks` field
  pointing to `hooks/codex-hooks.json` for plugin-oriented installs.
- The skill source of truth remains `paperer-skill-package/`.
- Hybrid mode (`docling-fast`) is enabled by default for better formula and
  table detection. The script falls back to local mode automatically if the
  hybrid server is not running.

