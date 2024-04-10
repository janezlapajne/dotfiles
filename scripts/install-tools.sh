#!/usr/bin/env bash
#
# Install various tools

set -e

source $DOTFILES_ZSH/utils/prints.sh

info "Installing tools -› scripts/install-tools.sh"

# Bat
sudo apt install -y bat
if [ ! -e ~/.local/bin/bat ]; then
	ln -s $(which batcat) ~/.local/bin/bat
else
	warn "Symbolic link ~/.local/bin/bat already exists."
fi

# Fd-find
sudo apt install -y fd-find
if [ ! -e ~/.local/bin/fd ]; then
	ln -s $(which fdfind) ~/.local/bin/fd
else
	warn "Symbolic link ~/.local/bin/fd already exists."
fi

# fkill
npm install --global fkill-cli

# pdm
curl -sSL https://pdm-project.org/install-pdm.py | python3 -

# The fuck
pip3 install thefuck --user --upgrade

# Tldr
pip3 install tldr

# zoxide
curl -sS https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | bash
