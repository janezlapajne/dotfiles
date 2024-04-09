#!/usr/bin/env bash
#
# Install various tools

set -e

source $DOTFILES_ZSH/utils/prints.sh

info "Installing tools -› scripts/install-tools.sh"

# pdm
curl -sSL https://pdm-project.org/install-pdm.py | python3 -

# zoxide
curl -sS https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | bash

# fkill
npm install --global fkill-cli

# The fuck
pip3 install thefuck --user --upgrade

# Tldr
pip3 install tldr

# Bat
sudo apt install bat
ln -s $(which batcat) ~/.local/bin/bat

# Fd-find
sudo apt install fd-find
ln -s $(which fdfind) ~/.local/bin/fd
