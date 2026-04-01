#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/paperer-skill-package/skills"
TARGET_DIR="$HOME/.agents/skills/paperer-skill-plugin"

mkdir -p "$HOME/.agents/skills"
ln -sfn "$SKILLS_DIR" "$TARGET_DIR"

echo "Installed Codex skills at $TARGET_DIR"

"$SCRIPT_DIR/install_deps.sh"

echo "Restart Codex to discover Paperer."

