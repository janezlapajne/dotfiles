# Load general paths first
export ZSH="$HOME/.oh-my-zsh"
export DOTFILES_ZSH=$HOME/.dotfiles
export DOTFILES_ROOT=$DOTFILES_ZSH/conf/dotfiles

# All .zsh files in dotfiles dir
typeset -U config_files
config_files=($DOTFILES_ROOT/**/*.zsh)

# 1.) Load the path files
for file in ${(M)config_files:#*/path.zsh}
do
  source $file
done

# 2.) Init Oh-My-Zsh before other configs so plugins/functions are available
source $DOTFILES_ROOT/zsh/omz-init.sh

# 3.) Load everything but the path and completion files
for file in ${${config_files:#*/path.zsh}:#*/completion.zsh}
do
  source $file
done

# 4.) Initialize autocomplete, otherwise functions won't be loaded
autoload -U compinit
compinit
# load every completion after autocomplete loads
for file in ${(M)config_files:#*/completion.zsh}
do
  source $file
done

unset config_files

# Load local config last so machine-specific overrides always win
if [[ -e ~/.localrc ]]; then
	source ~/.localrc
fi
