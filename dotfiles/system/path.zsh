# Preferred editor for local and remote sessions
if [[ -n $SSH_CONNECTION ]]; then
	export EDITOR='vim'
else
	export EDITOR='code'
fi

# Define variable if inside WSL
if grep -qEi "(Microsoft|WSL)" /proc/version &>/dev/null; then
	export INSIDE_WSL=1
else
	export INSIDE_WSL=0
fi
