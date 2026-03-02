# Preferred editor for local and remote sessions
if [[ -n $SSH_CONNECTION ]]; then
	export EDITOR='vim'
else
	export EDITOR='code'
fi

# Set the default PATH to include the dotfiles bin and local bin directories
export PATH="$DOTFILES_ZSH/conf/bin:$PATH"
export PATH="$HOME/.local/bin:$PATH"
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"

# Project folder that we can `c [tab]` to
export PROJECTS_DIR=~/programs
