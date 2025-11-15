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
	eza
	fzf-tab
	gh
	git
	ssh
	tmux
	uv
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

# fzf-tab
# disable sort when completing `git checkout`
zstyle ':completion:*:git-checkout:*' sort false
# set descriptions format to enable group support
# NOTE: don't use escape sequences (like '%F{red}%d%f') here, fzf-tab will ignore them
# zstyle ':completion:*:descriptions' format '[%d]'
# set list-colors to enable filename colorizing
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}
# force zsh not to show completion menu, which allows fzf-tab to capture the unambiguous prefix
zstyle ':completion:*' menu no
# preview directory's content with eza when completing cd
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'eza -1 --color=always $realpath'
# custom fzf flags
# NOTE: fzf-tab does not follow FZF_DEFAULT_OPTS by default
zstyle ':fzf-tab:*' fzf-flags --color=fg:1,fg+:2 --bind=tab:accept
# To make fzf-tab follow FZF_DEFAULT_OPTS.
# NOTE: This may lead to unexpected behavior since some flags break this plugin. See Aloxaf/fzf-tab#455.
zstyle ':fzf-tab:*' use-fzf-default-opts yes
# switch group using `<` and `>`
zstyle ':fzf-tab:*' switch-group '<' '>'

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
# setopt CORRECT
unsetopt correctall
unsetopt correct
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

# Init navi
eval "$(navi widget zsh)"

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
