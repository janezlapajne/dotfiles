#!/usr/bin/env bash
#
# Run all dotfiles installers.

set -e

source $DOTFILES_ZSH/utils/prints.sh

info "Running all installers -› scripts/install.sh"

find $DOTFILES_ROOT -name install.sh | while read installer; do
	if sh -c "${installer}"; then
		success "$installer executed successfully."
	else
		fail "Error executing $installer."
	fi
done
