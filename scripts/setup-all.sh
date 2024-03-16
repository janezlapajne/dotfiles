#!/usr/bin/env bash
#
# Run all setup scripts.

set -e

echo "Running all setup scripts"

# Find the setup scripts and run them iteratively
find $DOTFILES_ROOT -name setup.sh | while read setup; do sh -c "${setup}"; done
