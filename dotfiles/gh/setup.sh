#!/usr/bin/env bash

set -e

source $DOTFILES_ZSH/utils/prints.sh

info "Checking GitHub authentication status..."

if ! gh auth status -h github.com &>/dev/null; then
	info "Not logged in to GitHub, starting login process..."
	gh auth login --web -h github.com
	gh extension install github/gh-copilot
	gh extension install dlvhdr/gh-dash
	gh extension install https://github.com/nektos/gh-act
	success "Successfully logged in to GitHub."
else
	info "Already logged in to GitHub."
fi
