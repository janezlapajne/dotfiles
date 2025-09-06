# Oh-my-zsh configuration
ZSH_THEME="robbyrussell"
# ZSH_DISABLE_COMPFIX="true"
ENABLE_CORRECTION="true"
COMPLETION_WAITING_DOTS="true"
HIST_STAMPS="dd.mm.yyyy"

# Oh-my-zsh Plugins
plugins=(
	aliases
	alias-finder
	docker
	docker-compose
	gh
	git
	ssh
	tmux
	vi-mode
	zoxide
	zsh-interactive-cd
)

# vi-mode
VI_MODE_SET_CURSOR=true

# alias-finder
zstyle ':omz:plugins:alias-finder' autoload yes # disabled by default
zstyle ':omz:plugins:alias-finder' longer yes   # disabled by default
zstyle ':omz:plugins:alias-finder' exact yes    # disabled by default
zstyle ':omz:plugins:alias-finder' cheaper yes  # disabled by default

source $ZSH/oh-my-zsh.sh # ----> init oh-my-zsh
source $DOTFILES_ZSH/.env

# History
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000

# Setup options
setopt SHARE_HISTORY      # share history across sessions
setopt APPEND_HISTORY     # adds history
setopt INC_APPEND_HISTORY # adds history incrementally
setopt EXTENDED_HISTORY   # add timestamps to history
setopt HIST_VERIFY
setopt HIST_IGNORE_ALL_DUPS # don't record dupes in history
setopt HIST_REDUCE_BLANKS
# setopt NO_BG_NICE
# setopt NO_HUP
setopt LOCAL_OPTIONS # allow functions to have local options
setopt LOCAL_TRAPS   # allow functions to have local traps
setopt PROMPT_SUBST
setopt CORRECT
setopt COMPLETE_IN_WORD
setopt IGNORE_EOF
setopt NO_LIST_BEEP
unsetopt BEEP # Turn off all beeps

# Add functions to fpath
# chmod go-w "$DOTFILES_ZSH"
# chmod go-w "$DOTFILES_ZSH/functions"
fpath=($DOTFILES_ZSH/functions $fpath)
autoload -U $DOTFILES_ZSH/functions/*(:t)

# Init Atuin for better history
source "$HOME/.atuin/bin/env"
eval "$(atuin init zsh)"

# Init aliases for github copilot
eval "$(gh copilot alias -- zsh)"

# Init zoxide
eval "$(zoxide init zsh --cmd cd)"

# Init starship theme in terminal, else use default $ZSH_THEME
if [ "$TERMINAL_THEME_STARSHIP" = true ]; then
	eval "$(starship init zsh)"
fi

# We suggest using this y shell wrapper that provides the ability to change the current working directory when exiting Yazi.
function y() {
	local tmp="$(mktemp -t "yazi-cwd.XXXXXX")" cwd
	yazi "$@" --cwd-file="$tmp"
	IFS= read -r -d '' cwd < "$tmp"
	[ -n "$cwd" ] && [ "$cwd" != "$PWD" ] && builtin cd -- "$cwd"
	rm -f -- "$tmp"
}

