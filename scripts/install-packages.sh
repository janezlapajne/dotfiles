#!/usr/bin/env bash
#
# Install or update system packages

set -e

source $DOTFILES_ZSH/utils/prints.sh

info "Installing packages -› scripts/install-packages.sh"

# Detect operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
	# macOS
	info "Detected macOS - using Homebrew"

	# Check if Homebrew is installed
	if ! command -v brew &> /dev/null; then
		info "Installing Homebrew..."
		/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
	fi

	# Install Nerd Font for better terminal experience
	info "Installing Fira Code Nerd Font..."
	brew install --cask font-fira-code-nerd-font

	# List of packages to install on macOS
	packages=(
		curl
		fzf
		git
		gh
		httpie
		pipx
		python3
		tmux
		vim
		wget
		zsh
		ripgrep
		htop
		tlrc
		zoxide
		bat
		fd
		pdm
		uv
		jq
		lazydocker
		lazygit
		yazi
		ffmpeg
		p7zip
		poppler
		resvg
		imagemagick
	)

	# Update Homebrew and upgrade all packages
	brew update && brew upgrade

	# Install packages
	for package in "${packages[@]}"; do
		brew install "$package"
	done

else
	# Linux/WSL
	info "Detected Linux/WSL - using apt-get"

	# List of packages to install on Linux
	packages=(
		atop
		curl
		fzf
		git
		httpie
		pipx
		python3
		tmux
		vim
		wget
		xclip
		zsh
		ripgrep
	)

	# Update package list and upgrade all packages
	sudo apt-get update && sudo apt-get upgrade -y

	# Install packages
	for package in "${packages[@]}"; do
		sudo apt-get install -y "$package"
	done
fi
