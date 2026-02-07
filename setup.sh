#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
VENV_PY="$VENV_DIR/bin/python"
REQ_FILE="$SCRIPT_DIR/requirements.txt"

echo "🔧 Setting up virtual environment and installing requirements..."

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 not found. Please install Python 3."
  exit 1
fi

if [[ ! -x "$VENV_PY" ]]; then
  echo "➡️ Creating virtual environment at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

if [[ ! -f "$REQ_FILE" ]]; then
  echo "⚠️ requirements.txt not found at: $REQ_FILE"
  echo "   Nothing to install."
  exit 0
fi

echo "⬆️ Upgrading pip, setuptools, wheel..."
"$VENV_PY" -m pip install --upgrade pip setuptools wheel

echo "📦 Installing packages from $REQ_FILE..."
"$VENV_PY" -m pip install -r "$REQ_FILE"

echo "✅ Setup complete. Virtualenv: $VENV_DIR"
