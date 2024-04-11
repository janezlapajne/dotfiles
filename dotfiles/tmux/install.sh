#!/bin/sh

set -e

if [ -d "$HOME/.tmux" ]; then
	echo "Updating .tmux"
	cd $HOME/.tmux
	git pull
else
	echo "Cloning .tmux"
	git clone https://github.com/gpakosz/.tmux.git $HOME/.tmux
fi

cat $HOME/.tmux/.tmux.conf.local >$HOME/.dotfiles/dotfiles/tmux/.tmux.conf.local
cat $HOME/.tmux/.tmux.conf >$HOME/.dotfiles/dotfiles/tmux/.tmux.conf
