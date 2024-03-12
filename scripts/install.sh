#!/usr/bin/env bash
#
# Run all dotfiles installers.

set -e

cd "$(dirname $0)"/..

# Install system packages using apt-get
echo "› scripts/install-packages.sh"
$DOTFILES_ZSH/scripts/install-packages.sh

echo "running all installers"
# Find the installers and run them iteratively
find $DOTFILES_ROOT -name install.sh | while read installer; do sh -c "${installer}"; done
