#!/usr/bin/env bash

set -e

source $DOTFILES_ZSH/utils/prints.sh

info "Checking GitHub authentication status..."

if ! gh auth status -h github.com &>/dev/null; then
	info "Not logged in to GitHub, starting login process..."
	gh auth login --web -h github.com
	gh extension install github/gh-copilot
	success "Successfully logged in to GitHub."
else
	info "Already logged in to GitHub."
fi
