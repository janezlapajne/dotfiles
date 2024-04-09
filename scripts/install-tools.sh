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
