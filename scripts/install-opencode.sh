#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/paperer-skill-package/skills"
TARGET_DIR="$HOME/.config/opencode/skills/paperer-skill-plugin"

mkdir -p "$HOME/.config/opencode/skills"
ln -sfn "$SKILLS_DIR" "$TARGET_DIR"

echo "Installed OpenCode skills at $TARGET_DIR"
echo "Restart OpenCode to discover Paperer."

