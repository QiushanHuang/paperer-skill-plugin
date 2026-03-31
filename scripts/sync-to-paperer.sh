#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_DIR="$REPO_ROOT/paperer-skill-package/"
TARGET_REPO="${1:-/Users/joshua/LLM_Qiushan/skill_paper_slide}"
TARGET_DIR="$TARGET_REPO/paperer-skill-package/"

if [ ! -d "$TARGET_REPO/.git" ]; then
  echo "Target repo is not a git repository: $TARGET_REPO" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"
rsync -a --delete --exclude '.DS_Store' "$SOURCE_DIR" "$TARGET_DIR"

echo "Mirrored $SOURCE_DIR to $TARGET_DIR"

