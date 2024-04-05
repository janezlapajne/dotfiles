#!/bin/sh

set -e

if [ ! -d "$HOME/.tmux/plugins/tpm" ]; then
	echo "Installing Tmux Plugin Manager"
	git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
else
	echo "Tmux Plugin Manager already installed"
fi
