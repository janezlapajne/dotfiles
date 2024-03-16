#!/usr/bin/env zsh

# Install oh-my-zsh
if [ ! -d "$HOME/.oh-my-zsh" ]; then
	echo "Installing oh-my-zsh"
	sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
else
	echo "Oh-my-zsh already installed, updating..."
	source $HOME/.oh-my-zsh/oh-my-zsh.sh
	omz update
fi
