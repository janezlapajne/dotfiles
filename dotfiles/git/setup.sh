#!/usr/bin/env bash

set -e

source $DOTFILES_ZSH/utils/prints.sh

if ! [ -f $DOTFILES_ROOT/git/.gitconfig.local ]; then
	info 'Setup gitconfig'

	git_credential='cache'
	if [ "$(uname -s)" == "Darwin" ]; then
		git_credential='osxkeychain'
	fi

	sed -e "s/AUTHORNAME/$GIT_NAME/g" -e "s/AUTHOREMAIL/$GIT_EMAIL/g" -e "s/GIT_CREDENTIAL_HELPER/$git_credential/g" $DOTFILES_ROOT/git/.gitconfig.local.example >$DOTFILES_ROOT/git/.gitconfig.local

	success 'Gitconfig setup complete'
else
	warn 'Gitconfig already setup. Delete `.gitconfig.local` and run setup again to overwrite.'
fi
