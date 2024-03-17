#!/usr/bin/env bash
#
# Run all setup scripts.

set -e

source $DOTFILES_ZSH/utils/prints.sh

info "Running all setup scripts -> scripts/setup-all.sh"

# Find the setup scripts and run them iteratively
find $DOTFILES_ROOT -name setup.sh | while read setup; do
	if sh -c "${setup}"; then
		success "$setup executed successfully."
	else
		fail "Error executing $setup."
	fi
done
