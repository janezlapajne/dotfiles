# Reload settings
alias rr='exec zsh'

# Enable color support of grep
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

alias py='python3'

# Easy cd
alias .1='cd ../'
alias .2='cd ../../'
alias .3='cd ../../../'
alias .4='cd ../../../../'
alias .5='cd ../../../../../'

# Handy shortcuts
alias h='history'
alias j='jobs -l'
alias cls='clear'

# Confirmation
alias mv='mv -i'
alias cp='cp -i'
alias ln='ln -i'

# Become root
alias root='sudo -i'

# Reboot / halt / poweroff
alias reboot='sudo /sbin/reboot'
alias poweroff='sudo /sbin/poweroff'
alias halt='sudo /sbin/halt'
alias shutdown='sudo /sbin/shutdown'

# This one saved by butt so many times
alias wget='wget -c'

# Set some other defaults
alias df='df -H'
alias du='du -ch'

# Random commands
alias mkd='mkdir -pv'

# Copy to clipboard
alias clip='pbcopy'

# Worktrunk
alias wts='wt switch'
alias wtc='wt switch --create'
alias wtl='wt list --full'
alias wtr='wt remove'
