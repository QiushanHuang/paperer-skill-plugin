#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Install Python dependencies once (individual scripts skip if already done)
"$SCRIPT_DIR/install_deps.sh"

# Set flag so per-platform scripts don't re-run install_deps
export PAPERER_DEPS_INSTALLED=1

"$SCRIPT_DIR/install-codex.sh"
"$SCRIPT_DIR/install-opencode.sh"
"$SCRIPT_DIR/install-claude-code.sh"

echo "Installed Paperer for Codex, OpenCode, and Claude Code."

