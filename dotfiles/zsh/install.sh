#!/usr/bin/env zsh

set -e

# Install oh-my-zsh
if [ ! -d "$HOME/.oh-my-zsh" ]; then
	echo "Installing oh-my-zsh"
	sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
else
	echo "Oh-my-zsh already installed, updating..."
	source $HOME/.oh-my-zsh/oh-my-zsh.sh
	omz update
fi

# Install starship theme
source $DOTFILES_ZSH/.env
if [ "$TERMINAL_THEME_STARSHIP" = true ]; then
	curl -sS https://starship.rs/install.sh | sh -s -- -y
fi
