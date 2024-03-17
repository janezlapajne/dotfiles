# Load general paths first
source $HOME/.dotfiles/core/paths.sh

# Stash environment variables in ~/.localrc. This means they'll stay out
# of main dotfiles repository (which may be public, like this one)
if [[ -e ~/.localrc ]]; then
	source ~/.localrc
fi

# All .zsh files in dotfiles dir
typeset -U config_files
config_files=($DOTFILES_ROOT/**/*.zsh)

# 1.) Load the path files
for file in ${(M)config_files:#*/path.zsh}
do
  source $file
done

# 2.) Load everything but the path and completion files
for file in ${${config_files:#*/path.zsh}:#*/completion.zsh}
do
  source $file
done

# 3.) Initialize autocomplete, otherwise functions won't be loaded
autoload -U compinit
compinit
# load every completion after autocomplete loads
for file in ${(M)config_files:#*/completion.zsh}
do
  source $file
done

unset config_files

# Init Atuin for better history
eval "$(atuin init zsh)"