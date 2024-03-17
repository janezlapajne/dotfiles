#!/usr/bin/env bash
#
# Install or update system packages using apt-get

set -e

source $DOTFILES_ZSH/utils/prints.sh

info "Installing packages -› scripts/install-packages.sh"

# List of packages to install
packages=(
    git
    python3
    vim
    xclip
    zsh
    curl
    wget
    tmux
    atop
)

# Update package list and upgrade all packages
sudo apt-get update && sudo apt-get upgrade -y

# Install packages
for package in "${packages[@]}"; do
    sudo apt-get install -y "$package"
done
