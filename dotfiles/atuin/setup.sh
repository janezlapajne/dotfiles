#!/usr/bin/env sh

set -e

# Register to sync server
if [ -n "$ATUIN_USERNAME" ] && [ -n "$ATUIN_EMAIL" ] && [ -n "$ATUIN_PASSWORD" ] && [ -z "$ATUIN_KEY" ]; then
	atuin register -u $ATUIN_USERNAME -e $ATUIN_EMAIL -p $ATUIN_PASSWORD
	atuin import auto
	atuin sync
fi

# Login to sync server
if [ -n "$ATUIN_USERNAME" ] && [ -n "$ATUIN_PASSWORD" ] && [ -n "$ATUIN_KEY" ]; then
	atuin login -u $ATUIN_USERNAME -p $ATUIN_PASSWORD -k $ATUIN_KEY
	atuin sync
fi
