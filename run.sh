#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PY="$SCRIPT_DIR/.venv/bin/python"

echo "🚀 Starting Chinese Character Learning System..."
echo ""

if [[ ! -x "$VENV_PY" ]]; then
	echo "❌ Python virtual environment not found at: $VENV_PY"
	echo "   Please create it first or update the path."
	exit 1
fi

cd "$SCRIPT_DIR"
"$VENV_PY" -m modules.main
