#!/usr/bin/env bash

# List of packages to install
packages=(
    git
    python3
    vim
)

# Update package list and upgrade all packages
sudo apt-get update && sudo apt-get upgrade -y

# Install packages
for package in "${packages[@]}"; do
    sudo apt-get install -y "$package"
done