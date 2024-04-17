#!/bin/sh

set -e

if [ -d "$HOME/.vim_runtime" ]; then
	echo "Updating .vim_runtime"
	(
		cd $HOME/.vim_runtime
		git reset --hard
		git clean -d --force
		git pull --rebase
		python3 update_plugins.py
	)
else
	echo "Cloning .vim_runtime"
	git clone --depth=1 https://github.com/amix/vimrc.git $HOME/.vim_runtime
fi
