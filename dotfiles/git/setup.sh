#!/usr/bin/env bash

set -e

source $DOTFILES_ZSH/utils/prints.sh

if ! [ -f $DOTFILES_ROOT/git/.gitconfig.local ]; then
	info 'Setup gitconfig'

	git_credential='cache'

	sed -e "s|USER_NAME|$GIT_NAME|g" \
		-e "s|USER_EMAIL|$GIT_EMAIL|g" \
		-e "s|CREDENTIAL_HELPER|$GIT_CREDENTIAL_HELPER|g" \
		$DOTFILES_ROOT/git/.gitconfig.local.example >$DOTFILES_ROOT/git/.gitconfig.local

	success 'Gitconfig setup complete'
else
	warn 'Gitconfig already setup. Delete `.gitconfig.local` and run setup again to overwrite.'
fi
