#!/usr/bin/env bash

set -e

source $DOTFILES_ZSH/utils/prints.sh

# Register to sync server
if [ -n "$ATUIN_USERNAME" ] && [ -n "$ATUIN_EMAIL" ] && [ -n "$ATUIN_PASSWORD" ] && [ -z "$ATUIN_KEY" ]; then
	info "Registering to sync server..."
	atuin register -u $ATUIN_USERNAME -e $ATUIN_EMAIL -p $ATUIN_PASSWORD
	atuin import auto
	atuin sync
	success "Registration and sync successful."
elif [ -n "$ATUIN_KEY" ]; then
	info "Key found. Skipping registration."
else
	fail "Registration failed. Please ensure ATUIN_USERNAME, ATUIN_EMAIL, and ATUIN_PASSWORD are set."
fi

# Login to sync server
if [ -n "$ATUIN_USERNAME" ] && [ -n "$ATUIN_PASSWORD" ] && [ -n "$ATUIN_KEY" ]; then
	info "Logging in to sync server..."
	atuin login -u $ATUIN_USERNAME -p $ATUIN_PASSWORD -k $ATUIN_KEY
	atuin sync
	success "Login and sync successful."
else
	warn "Login not succesful. Please ensure ATUIN_USERNAME, ATUIN_PASSWORD, and ATUIN_KEY are set."
fi
