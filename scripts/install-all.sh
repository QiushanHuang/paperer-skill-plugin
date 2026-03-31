#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

"$SCRIPT_DIR/install-codex.sh"
"$SCRIPT_DIR/install-opencode.sh"
"$SCRIPT_DIR/install-claude-code.sh"

echo "Installed Paperer for Codex, OpenCode, and Claude Code."

