#!/usr/bin/env bash

set -e

if command -v atuin >/dev/null 2>&1; then
	echo "Atuin already installed"
else
	echo "Installing Atuin"
	bash <(curl --proto '=https' --tlsv1.2 -sSf https://setup.atuin.sh)
fi
