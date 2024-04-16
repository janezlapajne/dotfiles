#!/bin/sh

set -e

if [ -d "$HOME/.tmux" ]; then
	echo "Updating .tmux"
	(
		cd $HOME/.tmux
		git pull
	)
else
	echo "Cloning .tmux"
	git clone --depth=1 https://github.com/gpakosz/.tmux.git $HOME/.tmux
fi

cat $HOME/.tmux/.tmux.conf.local >$DOTFILES_ROOT/tmux/tmux.conf.local
cat $HOME/.tmux/.tmux.conf >$DOTFILES_ROOT/tmux/.tmux.conf
