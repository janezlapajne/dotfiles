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
	# zsh-navigation-tools
	vi-mode
	# z
	tmux
)

source $ZSH/oh-my-zsh.sh

# History
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt SHARE_HISTORY

# Turn off all beeps
unsetopt BEEP

# Use vim keys in tab complete menu:
bindkey -M menuselect 'h' vi-backward-char
bindkey -M menuselect 'k' vi-up-line-or-history
bindkey -M menuselect 'l' vi-forward-char
bindkey -M menuselect 'j' vi-down-line-or-history
bindkey -v '^?' backward-delete-char

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

# Edit line in vim with ctrl-e:
autoload -z edit-command-line
zle -N edit-command-line
bindkey '^e' edit-command-line
