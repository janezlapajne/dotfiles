from dataclasses import dataclass, field
from pathlib import Path

from dotenv import dotenv_values

DOTFILES_REPO = ".dotfiles"
CONF_DIR = "conf"
DOTFILES_SUBDIR = "dotfiles"
ENV_FILE = ".env"
ENV_EXAMPLE_FILE = ".env.example"
PACKAGES_FILE = "packages.toml"
SYMLINKS_FILE = "symlinks.toml"
DEFAULT_EDITOR = "vim"

OH_MY_ZSH_DIR = ".oh-my-zsh"
SSH_DIR = ".ssh"
SSH_KEY_FILE = "id_rsa"
TMUX_DIR = ".tmux"
VIM_RUNTIME_DIR = ".vim_runtime"

GIT_MODULE = "git"
TMUX_MODULE = "tmux"
GITCONFIG_LOCAL = ".gitconfig.local"
GITCONFIG_LOCAL_EXAMPLE = ".gitconfig.local.example"
TMUX_CONF = ".tmux.conf"
TMUX_CONF_LOCAL = ".tmux.conf.local"
TMUX_CONF_LOCAL_TEMPLATE = "tmux.conf.local"


@dataclass(frozen=True)
class Config:
    dotfiles_zsh: Path = field(default_factory=lambda: Path.home() / DOTFILES_REPO)
    home: Path = field(default_factory=Path.home)
    env: dict[str, str] = field(default_factory=dict)

    @property
    def conf_dir(self) -> Path:
        return self.dotfiles_zsh / CONF_DIR

    @property
    def env_file(self) -> Path:
        return self.dotfiles_zsh / ENV_FILE

    @property
    def env_example_file(self) -> Path:
        return self.dotfiles_zsh / ENV_EXAMPLE_FILE

    @property
    def packages_file(self) -> Path:
        return self.conf_dir / PACKAGES_FILE

    @property
    def symlinks_file(self) -> Path:
        return self.conf_dir / SYMLINKS_FILE

    @property
    def dotfiles_root(self) -> Path:
        return self.conf_dir / DOTFILES_SUBDIR

    @property
    def oh_my_zsh_dir(self) -> Path:
        return self.home / OH_MY_ZSH_DIR

    @property
    def ssh_key_path(self) -> Path:
        return self.home / SSH_DIR / SSH_KEY_FILE

    @property
    def tmux_dir(self) -> Path:
        return self.home / TMUX_DIR

    @property
    def vim_runtime_dir(self) -> Path:
        return self.home / VIM_RUNTIME_DIR

    @property
    def git_module_dir(self) -> Path:
        return self.dotfiles_root / GIT_MODULE

    @property
    def tmux_module_dir(self) -> Path:
        return self.dotfiles_root / TMUX_MODULE

    @classmethod
    def load(cls) -> "Config":
        dotfiles_zsh = Path.home() / DOTFILES_REPO
        env = {k: v for k, v in dotenv_values(dotfiles_zsh / ENV_FILE).items() if v}
        return cls(dotfiles_zsh=dotfiles_zsh, env=env)
