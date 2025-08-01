#!/usr/bin/env bash
#
# bootstrap installs things.

cd "$(dirname "$0")"
source ./core/paths.sh
source $DOTFILES_ZSH/utils/prints.sh
source $DOTFILES_ZSH/core/setup-dotfiles.sh

set -e

echo ''

info "Installing dependencies"
if source $DOTFILES_ZSH/bin/dot | while read -r data; do info "$data"; done; then
	success "Dependencies installed"
else
	fail "Error installing dependencies"
fi

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

# Link all the dotfiles
setup_dotfiles

echo ''
echo '  Done!'
