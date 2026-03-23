# Completion: disable sort when completing `git checkout`
zstyle ':completion:*:git-checkout:*' sort false
# Completion: enable filename colorizing
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}
# Completion: disable menu so fzf-tab can capture the unambiguous prefix
zstyle ':completion:*' menu no

# fzf-tab: preview directory content with eza when completing cd
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'eza -1 --color=always $realpath'
# fzf-tab: custom fzf flags
zstyle ':fzf-tab:*' fzf-flags --color=fg:1,fg+:2 --bind=tab:accept
# fzf-tab: follow FZF_DEFAULT_OPTS
# NOTE: This may lead to unexpected behavior since some flags break this plugin. See Aloxaf/fzf-tab#455.
zstyle ':fzf-tab:*' use-fzf-default-opts yes
# fzf-tab: switch group using `<` and `>`
zstyle ':fzf-tab:*' switch-group '<' '>'
