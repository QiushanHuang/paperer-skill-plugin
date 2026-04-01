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
INSTALL_PYTHON=""
INSTALL_PIP=""

# If already inside a venv, install directly
if [ -n "${VIRTUAL_ENV:-}" ]; then
  echo "Installing Python dependencies into active venv ($VIRTUAL_ENV) …"
  INSTALL_PYTHON="${VIRTUAL_ENV}/bin/python"
  INSTALL_PIP="${VIRTUAL_ENV}/bin/pip"

  if [ ! -x "$INSTALL_PYTHON" ]; then
    INSTALL_PYTHON="$PYTHON"
  fi

  if [ ! -x "$INSTALL_PIP" ]; then
    if command -v pip &>/dev/null; then
      INSTALL_PIP="$(command -v pip)"
    else
      echo "WARNING: pip not found in active venv."
      exit 0
    fi
  fi

  "$INSTALL_PIP" install -r "$REQ_FILE" && {
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
  INSTALL_PYTHON="$VENV_DIR/bin/python"
  INSTALL_PIP="$VENV_DIR/bin/pip"

  "$INSTALL_PIP" install -r "$REQ_FILE" && {
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

HYBRID_READY=0
echo "Installing hybrid extras for docling-fast …"
"$INSTALL_PIP" install "opendataloader-pdf[hybrid]>=2.0" && {
  echo "Hybrid extras installed successfully."
  HYBRID_READY=1
} || {
  echo "WARNING: hybrid dependency install failed."
  echo "Hybrid mode may fall back to local processing until this succeeds."
}

if [ "$HYBRID_READY" = "1" ]; then
  echo "Pre-downloading EasyOCR models for hybrid mode …"
  if "$INSTALL_PYTHON" "$REPO_ROOT/scripts/warmup_hybrid_models.py"; then
    echo "Hybrid OCR models are cached locally."
  else
    echo "WARNING: hybrid model warmup failed."
    echo "The first docling-fast run may still need network access."
  fi
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
