#!/bin/sh

set -e

# install/update lazy docker - skip on macOS (Darwin)
if [[ "$OSTYPE" != "darwin"* ]]; then
	curl https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | bash
else
	echo "Skipping lazy docker installation on macOS (Darwin)"
fi
