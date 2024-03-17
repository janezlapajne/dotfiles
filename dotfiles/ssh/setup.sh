#!/usr/bin/env bash

set -e

source $DOTFILES_ZSH/utils/prints.sh

if ! [ -f ~/.ssh/id_rsa ]; then
	info 'Setup ssh key'
	if [ -z $SSH_PASSPHRASE ]; then
		ssh-keygen -t rsa -b 4096 -C $SSH_EMAIL -f ~/.ssh/id_rsa
	else
		ssh-keygen -t rsa -b 4096 -C $SSH_EMAIL -N $SSH_PASSPHRASE -f ~/.ssh/id_rsa
	fi
	success 'SSH key setup successful'
else
	warn 'SSH key already setup. Delete `~/.ssh/id_rsa` and run setup again to overwrite.'
fi
