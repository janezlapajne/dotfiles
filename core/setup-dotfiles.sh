#!/bin/sh

link_file() {
	local src=$1 dst=$2

	local overwrite= backup= skip=
	local action=

	if [ -f "$dst" -o -d "$dst" -o -L "$dst" ]; then

		if [ "$overwrite_all" == "false" ] && [ "$backup_all" == "false" ] && [ "$skip_all" == "false" ]; then

			local currentSrc="$(readlink $dst)"

			if [ "$currentSrc" == "$src" ]; then

				skip=true

			else

				user "File already exists: $dst ($(basename "$src")), what do you want to do?\n\
        [s]kip, [S]kip all, [o]verwrite, [O]verwrite all, [b]ackup, [B]ackup all?"
				read -n 1 action

				case "$action" in
				o)
					overwrite=true
					;;
				O)
					overwrite_all=true
					;;
				b)
					backup=true
					;;
				B)
					backup_all=true
					;;
				s)
					skip=true
					;;
				S)
					skip_all=true
					;;
				*) ;;
				esac

			fi

		fi

		overwrite=${overwrite:-$overwrite_all}
		backup=${backup:-$backup_all}
		skip=${skip:-$skip_all}

		if [ "$overwrite" == "true" ]; then
			rm -rf "$dst"
			success "removed $dst"
		fi

		if [ "$backup" == "true" ]; then
			mv "$dst" "${dst}.backup"
			success "moved $dst to ${dst}.backup"
		fi

		if [ "$skip" == "true" ]; then
			success "skipped $src"
		fi
	fi

	if [ "$skip" != "true" ]; then # "false" or empty
		ln -s "$src" "$dst"
		success "linked $src to $dst"
	fi
}

setup_dotfiles() {
	info 'installing dotfiles'

	local overwrite_all=false backup_all=false skip_all=false

	for src in $(find -H "$DOTFILES_ROOT" -maxdepth 2 -name '.*' -not -path "*.zsh" -not -path "*.sh" -not -path "*.example"); do
		dst="$HOME/$(basename "${src}")"
		info "$src -> $dst"
		link_file "$src" "$dst"
	done
}
