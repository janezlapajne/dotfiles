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
