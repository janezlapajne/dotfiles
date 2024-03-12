#!/usr/bin/env bash
#
# bootstrap installs things.

# cd "$(dirname "$0")/.."
source $(pwd -P)/utils/constants.sh
source $DOTFILES_ZSH/utils/prints.sh
source $DOTFILES_ZSH/utils/setup-dotfiles.sh
source $DOTFILES_ROOT/git/setup.sh

set -e

echo ''

# setup_gitconfig
setup_dotfiles

# If we're on a linux
if [ "$(uname -s)" == "Linux" ]; then
  info "installing dependencies"
  if source $DOTFILES_ZSH/bin/dot | while read -r data; do info "$data"; done; then
    success "dependencies installed"
  else
    fail "error installing dependencies"
  fi
fi

echo ''
echo '  All installed!'
