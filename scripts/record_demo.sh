#!/usr/bin/env bash
# record_demo.sh - record the README demo GIF using VHS.
#
# Usage:
#   bash scripts/record_demo.sh
#
# Requires VHS (https://github.com/charmbracelet/vhs).
# Output: docs/demo.gif (embedded in README).

set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v vhs &>/dev/null; then
    echo "Error: vhs is not installed."
    echo ""
    echo "Install with:"
    echo "  brew install vhs          # macOS"
    echo "  sudo snap install vhs     # Linux"
    echo "  go install github.com/charmbracelet/vhs@latest  # Go"
    exit 1
fi

if [[ ! -d .venv ]]; then
    echo "Error: .venv not found. Run 'make install' first."
    exit 1
fi

mkdir -p docs

echo "Recording demo GIF..."
vhs scripts/demo.tape

echo ""
echo "Done: docs/demo.gif"
echo ""
echo "To embed in README, add this line to the top of the README body:"
echo "  ![demo](docs/demo.gif)"
