#!/usr/bin/env bash
#
# Run all dotfiles installers.

set -e

echo "Running all installers"
# Find the installers and run them iteratively
find $DOTFILES_ROOT -name install.sh | while read installer; do sh -c "${installer}"; done
