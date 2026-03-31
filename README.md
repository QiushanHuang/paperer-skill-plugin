# paperer-skill-plugin

`paperer-skill-plugin` is the cross-platform distribution repository for the
minimal `Paperer` skill package.

It keeps the actual skill source in `paperer-skill-package/` and adds the
platform-specific wrapper files needed to make the package easy to install in:

- Codex
- Claude Code
- OpenCode

## Repository layout

- `paperer-skill-package/`
  - canonical skill package mirrored back into the original `Paperer` repo
- `.codex-plugin/plugin.json`
  - Codex plugin metadata
- `.claude-plugin/plugin.json`
  - Claude plugin metadata
- `.claude/commands/paperer.md`
  - Claude Code slash-command entry
- `.claude/agents/paperer.md`
  - Claude Code agent wrapper
- `.opencode/plugins/paperer-skill-plugin.js`
  - OpenCode plugin entry that auto-registers the bundled skills
- `.codex/INSTALL.md`
  - Codex installation guide
- `.opencode/INSTALL.md`
  - OpenCode installation guide
- `scripts/`
  - local install helpers and mirror sync tooling

## Installation

### Codex

Follow [.codex/INSTALL.md](.codex/INSTALL.md).

### OpenCode

Follow [.opencode/INSTALL.md](.opencode/INSTALL.md).

### Claude Code

Run:

```bash
./scripts/install-claude-code.sh
```

This installs:

- the bundled skills into `~/.claude/skills/paperer-skill-plugin`
- `/paperer` as a slash command
- `paperer` as a local Claude agent wrapper

## Source of truth

This repository is the public source of truth for the distributable Paperer
skill package.

The original `Paperer` repository receives the mirrored subtree at:

`paperer-skill-package/`

## Mirroring back into `Paperer`

Run:

```bash
./scripts/sync-to-paperer.sh /absolute/path/to/Paperer
```

If no path is provided, the script defaults to:

`/Users/joshua/LLM_Qiushan/skill_paper_slide`

