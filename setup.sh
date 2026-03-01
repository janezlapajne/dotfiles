#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

# Ensure uv is available
if ! command -v uv &>/dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install the dotfiles package as a uv tool (editable mode)
uv tool install --editable . --force

# Run the full bootstrap
dotfiles setup
