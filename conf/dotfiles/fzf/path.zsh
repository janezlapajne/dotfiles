# FZF: use fd as default source (faster than find, respects .gitignore)
export FZF_DEFAULT_COMMAND="fd --hidden --strip-cwd-prefix --exclude .git"
# Ctrl+T: fuzzy find files and insert path at cursor (with bat preview)
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
# Esc+C: fuzzy find directories and cd into selection (with tree preview)
export FZF_ALT_C_COMMAND="fd --type=d --hidden --strip-cwd-prefix --exclude .git"

# FZF: appearance (applies globally to all fzf usage)
export FZF_DEFAULT_OPTS="--height 50% --layout=default --border --color=hl:#2dd4bf"

# FZF: previews
export FZF_CTRL_T_OPTS="--preview 'bat --color=always -n --line-range :500 {}'"
export FZF_ALT_C_OPTS="--preview 'eza --icons=always --tree --color=always {} | head -200'"
