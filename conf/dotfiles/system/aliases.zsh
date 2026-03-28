# Reload settings
alias rr='exec zsh'

# Enable color support of grep
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

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
alias rp='realpath'

# Copy to clipboard
alias clip='pbcopy'

# Process management
alias fk='fkill'

# Modern ls with eza
alias ls="eza --no-filesize --long --color=always --icons=always --no-user"

# Tree views (eza-based)
alias tree="eza --tree --level=3 --icons=always --color=always -a --ignore-glob='.git'"
alias dtree="eza --tree --level=3 --icons=always --color=always -a -D --ignore-glob='.git'"

# Fuzzy find and open man pages
alias fman="compgen -c | fzf | xargs man"

# Other
alias idea='open -a "IntelliJ IDEA"'
alias cl='claude'
