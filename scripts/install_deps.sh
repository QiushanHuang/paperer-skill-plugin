#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REQ_FILE="$REPO_ROOT/requirements.txt"

if [ "${PAPERER_DEPS_INSTALLED:-}" = "1" ]; then
  exit 0
fi

if [ ! -f "$REQ_FILE" ]; then
  echo "requirements.txt not found at $REQ_FILE — skipping dependency install."
  exit 0
fi

PYTHON=""
for candidate in python3 python; do
  if command -v "$candidate" &>/dev/null; then
    PYTHON="$candidate"
    break
  fi
done

if [ -z "$PYTHON" ]; then
  echo "WARNING: python not found. Python dependencies were not installed."
  echo "Install Python 3.10+ and retry."
  exit 0
fi

VENV_DIR="$REPO_ROOT/.venv"

# If already inside a venv, install directly
if [ -n "${VIRTUAL_ENV:-}" ]; then
  echo "Installing Python dependencies into active venv ($VIRTUAL_ENV) …"
  pip install -r "$REQ_FILE" && {
    echo "Python dependencies installed successfully."
  } || {
    echo "WARNING: pip install failed inside venv."
    exit 0
  }
else
  # Create project-local venv and install there
  if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR …"
    $PYTHON -m venv "$VENV_DIR"
  fi

  echo "Installing Python dependencies into $VENV_DIR …"
  "$VENV_DIR/bin/pip" install -r "$REQ_FILE" && {
    echo "Python dependencies installed successfully."
  } || {
    echo "WARNING: pip install failed. You can retry manually:"
    echo "  $VENV_DIR/bin/pip install -r $REQ_FILE"
    exit 0
  }

  echo ""
  echo "To use the extraction script, run:"
  echo "  $VENV_DIR/bin/python scripts/extract_assets.py <paper.pdf>"
  echo ""
  echo "Or activate the venv first:"
  echo "  source $VENV_DIR/bin/activate"
fi

# Verify or install Java (required by opendataloader-pdf)
if ! command -v java &>/dev/null; then
  echo "Java not found. opendataloader-pdf requires Java 11+."

  JAVA_INSTALLED=0

  # macOS — try Homebrew
  if [ "$(uname)" = "Darwin" ] && command -v brew &>/dev/null; then
    echo "Installing Java 11 via Homebrew …"
    if brew install openjdk@11; then
      # Symlink so the system JVM picker can find it
      sudo ln -sfn "$(brew --prefix openjdk@11)/libexec/openjdk.jdk" \
        /Library/Java/JavaVirtualMachines/openjdk-11.jdk 2>/dev/null || true
      echo "Java 11 installed via Homebrew."
      JAVA_INSTALLED=1
    else
      echo "WARNING: brew install openjdk@11 failed."
    fi

  # Debian/Ubuntu
  elif command -v apt-get &>/dev/null; then
    echo "Installing Java 11 via apt-get …"
    if sudo apt-get install -y openjdk-11-jre-headless 2>/dev/null; then
      echo "Java 11 installed via apt-get."
      JAVA_INSTALLED=1
    else
      echo "WARNING: apt-get install openjdk-11-jre-headless failed."
    fi

  # Fedora/RHEL/CentOS (dnf)
  elif command -v dnf &>/dev/null; then
    echo "Installing Java 11 via dnf …"
    if sudo dnf install -y java-11-openjdk-headless 2>/dev/null; then
      echo "Java 11 installed via dnf."
      JAVA_INSTALLED=1
    else
      echo "WARNING: dnf install java-11-openjdk-headless failed."
    fi

  # Older CentOS/RHEL (yum)
  elif command -v yum &>/dev/null; then
    echo "Installing Java 11 via yum …"
    if sudo yum install -y java-11-openjdk-headless 2>/dev/null; then
      echo "Java 11 installed via yum."
      JAVA_INSTALLED=1
    else
      echo "WARNING: yum install java-11-openjdk-headless failed."
    fi
  fi

  if [ "$JAVA_INSTALLED" = "0" ]; then
    echo "WARNING: Could not install Java automatically."
    echo "Install Java 11+ manually:"
    echo "  - Download: https://adoptium.net/"
    echo "  - macOS:    brew install openjdk@11"
    echo "  - Ubuntu:   sudo apt-get install openjdk-11-jre-headless"
    echo "  - Fedora:   sudo dnf install java-11-openjdk-headless"
  fi
fi
