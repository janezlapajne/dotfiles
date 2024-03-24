# Reload settings
alias rr='. ~/.zshrc'

# Enable color support of ls and also add handy aliases
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Some more ls aliases
alias ls='ls -hN --color=auto --group-directories-first'
alias l.='ls -d .* --color=auto'

# WSL specific
alias note='cmd.exe /C start notepad.exe'
alias exe='explorer.exe'
alias py='python3'

# Easy cd
alias .1='cd ../'
alias .2='cd ../../'
alias .3='cd ../../../'
alias .4='cd ../../../../'
alias .5='cd ../../../../../'

# Colorize the grep command output for ease of use
alias grep='grep --color=auto'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'

# Handy shortcuts
alias h='history'
alias j='jobs -l'
alias cls='clear'

# Confirmation
alias mv='mv -i'
alias cp='cp -i'
alias ln='ln -i'

# Parenting changing perms on /
alias chown='chown --preserve-root'
alias chmod='chmod --preserve-root'
alias chgrp='chgrp --preserve-root'

# Become root
alias root='sudo -i'

# Reboot / halt / poweroff
alias reboot='sudo /sbin/reboot'
alias poweroff='sudo /sbin/poweroff'
alias halt='sudo /sbin/halt'
alias shutdown='sudo /sbin/shutdown'

# Pass options to free
alias meminfo='free -m -l -t'

# Get top process eating memory
alias psmem='ps auxf | sort -nr -k 4'
alias psmem10='ps auxf | sort -nr -k 4 | head -10'

# Get top process eating cpu
alias pscpu='ps auxf | sort -nr -k 3'
alias pscpu10='ps auxf | sort -nr -k 3 | head -10'

# Get server cpu info
alias cpuinfo='lscpu'

# Get GPU ram on desktop / laptop
alias gpumeminfo='grep -i --color memory /var/log/Xorg.0.log'

# This one saved by butt so many times
alias wget='wget -c'

# Set some other defaults
alias df='df -H'
alias du='du -ch'

# Top is atop, just like vi is vim
alias top='atop'

# Read absolute path of a file
alias rdirn='readlink -f'

# Random commands
alias mkd='mkdir -pv'
alias ccat='highlight --out-format=ansi'
