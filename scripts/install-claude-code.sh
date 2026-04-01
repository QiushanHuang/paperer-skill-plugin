#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/paperer-skill-package/skills"
COMMAND_FILE="$REPO_ROOT/.claude/commands/paperer.md"
AGENT_FILE="$REPO_ROOT/.claude/agents/paperer.md"

mkdir -p "$HOME/.claude/skills" "$HOME/.claude/commands" "$HOME/.claude/agents"

ln -sfn "$SKILLS_DIR" "$HOME/.claude/skills/paperer-skill-plugin"
ln -sfn "$COMMAND_FILE" "$HOME/.claude/commands/paperer.md"
ln -sfn "$AGENT_FILE" "$HOME/.claude/agents/paperer.md"

echo "Installed Claude Code wrappers and skills."

"$SCRIPT_DIR/install_deps.sh"

echo "Restart Claude Code to discover /paperer and the local paperer agent."

