#!/bin/sh

set -e

# Install/upgrade github cli
sudo mkdir -p -m 755 /etc/apt/keyrings && wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null &&
	sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg &&
	echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null &&
	sudo apt update &&
	sudo apt install gh -y

# Update copilot extension
if gh auth status >/dev/null 2>&1; then
	echo "User is logged in. Updating copilot extension..."
	gh extension upgrade copilot
else
	echo "User is not logged in. Skipping copilot extension upgrade."
fi
