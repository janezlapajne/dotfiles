# OH-MY-ZSH configuration
ZSH_THEME="robbyrussell"
# ZSH_DISABLE_COMPFIX="true"
ENABLE_CORRECTION="true"
COMPLETION_WAITING_DOTS="true"
HIST_STAMPS="dd.mm.yyyy"

# Plugins
# Download zip (do not clone) and extract to .oh-my-zsh\custom\plugins + rename
# Must have unix line ending
plugins=(
	git
	zsh-interactive-cd
	zsh-navigation-tools
	vi-mode
	z
	tmux
)

source $ZSH/oh-my-zsh.sh

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

# Use vim keys in tab complete menu:
bindkey -M menuselect 'h' vi-backward-char
bindkey -M menuselect 'k' vi-up-line-or-history
bindkey -M menuselect 'l' vi-forward-char
bindkey -M menuselect 'j' vi-down-line-or-history
bindkey -v '^?' backward-delete-char

# Add functions to fpath
chmod go-w "$DOTFILES_ZSH"
chmod go-w "$DOTFILES_ZSH/functions"
fpath=($DOTFILES_ZSH/functions $fpath)
autoload -U $DOTFILES_ZSH/functions/*(:t)

# Change cursor shape for different vi modes.
function zle-keymap-select() {
	case $KEYMAP in
	vicmd) echo -ne '\e[1 q' ;;        # block
	viins | main) echo -ne '\e[5 q' ;; # beam
	esac
}
zle -N zle-keymap-select
zle-line-init() {
	zle -K viins # initiate `vi insert` as keymap (can be removed if `bindkey -V` has been set elsewhere)
	echo -ne "\e[5 q"
}
zle -N zle-line-init
echo -ne '\e[5 q'                # Use beam shape cursor on startup.
preexec() { echo -ne '\e[5 q'; } # Use beam shape cursor for each new prompt.

# vi mode
bindkey -v
export KEYTIMEOUT=1

# Edit line in code with ctrl-e:
autoload -z edit-command-line
zle -N edit-command-line
bindkey '^e' edit-command-line

# Init Atuin for better history
eval "$(atuin init zsh)"

# Init aliases for github copilot
eval "$(gh copilot alias -- zsh)"
