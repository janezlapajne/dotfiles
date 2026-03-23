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
	fzf
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

source $ZSH/oh-my-zsh.sh # ----> init oh-my-zsh
