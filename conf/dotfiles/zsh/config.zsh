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
# unsetopt BEEP # Turn off all beeps

# Prefix-based history navigation in vi insert mode
# Type a prefix then Ctrl+P/N to cycle matching history entries
autoload -U up-line-or-beginning-search down-line-or-beginning-search
zle -N up-line-or-beginning-search
zle -N down-line-or-beginning-search
bindkey -M viins '^P' up-line-or-beginning-search
bindkey -M viins '^N' down-line-or-beginning-search

# Add functions to fpath
# chmod go-w "$DOTFILES_ZSH"
# chmod go-w "$DOTFILES_ZSH/functions"
fpath=($DOTFILES_ZSH/conf/functions $fpath)
autoload -U $DOTFILES_ZSH/conf/functions/*(:t)

# Init Atuin for better history
source "$HOME/.atuin/bin/env"
eval "$(atuin init zsh)"

# Init zoxide
eval "$(zoxide init zsh --cmd cd)"

# Init navi
eval "$(navi widget zsh)"

# Init Homebrew
eval "$(brew shellenv)"

# Init worktrunk
eval "$(wt config shell init zsh)"

# Init starship theme in terminal, else use default $ZSH_THEME
if grep -q '^TERMINAL_THEME_STARSHIP=true$' "$DOTFILES_ZSH/.env" 2>/dev/null; then
	eval "$(starship init zsh)"
fi
