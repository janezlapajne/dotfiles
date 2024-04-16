#!/usr/bin/env bash

set -e

source $DOTFILES_ZSH/utils/prints.sh

if ! [ -f $DOTFILES_ROOT/tmux/.tmux.conf.local ]; then
	info 'Setup tmux config'
	cp $DOTFILES_ROOT/tmux/tmux.conf.local $DOTFILES_ROOT/tmux/.tmux.conf.local
	success 'Setup complete'
else
	warn 'Local tmux already setup. Delete `$DOTFILES_ROOT/tmux/.tmux.conf.local` and run setup again to overwrite.'
fi
