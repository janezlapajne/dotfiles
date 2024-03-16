#!/usr/bin/env bash

set -e

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
)

# Update package list and upgrade all packages
sudo apt-get update && sudo apt-get upgrade -y

# Install packages
for package in "${packages[@]}"; do
    sudo apt-get install -y "$package"
done
