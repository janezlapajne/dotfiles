#!/usr/bin/env bash
#
# bootstrap installs things.

cd "$(dirname "$0")"
source ./utils/paths.sh
source $DOTFILES_ZSH/utils/prints.sh
source $DOTFILES_ZSH/utils/setup-dotfiles.sh

set -e

echo ''

# If we're on a linux
if [ "$(uname -s)" == "Linux" ]; then
  info "installing dependencies"
  if source $DOTFILES_ZSH/bin/dot | while read -r data; do info "$data"; done; then
    success "dependencies installed"
  else
    fail "error installing dependencies"
  fi
fi

# Link all the dotfiles
setup_dotfiles

# Export variables defined in .env
while IFS='=' read -r key value; do
  # if key and value not empty:
  if [ -n "$key" ] && [ -n "$value" ]; then
    export $key=$value
  fi
done <.env

# Run all setup scripts
if source $DOTFILES_ZSH/scripts/setup-all.sh | while read -r data; do info "$data"; done; then
  success "Setup scripts executed successfully."
else
  fail "Error executing setup scripts."
fi

echo ''
echo '  All installed!'
