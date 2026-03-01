from dataclasses import dataclass, field
from pathlib import Path

from dotenv import dotenv_values

DOTFILES_REPO = ".dotfiles"
CONF_DIR = "conf"
DOTFILES_SUBDIR = "dotfiles"
ENV_FILE = ".env"
ENV_EXAMPLE_FILE = ".env.example"
PACKAGES_FILE = "packages.toml"
DEFAULT_EDITOR = "vim"


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
    def dotfiles_root(self) -> Path:
        return self.conf_dir / DOTFILES_SUBDIR

    @classmethod
    def load(cls) -> "Config":
        dotfiles_zsh = Path.home() / DOTFILES_REPO
        env = {k: v for k, v in dotenv_values(dotfiles_zsh / ENV_FILE).items() if v}
        return cls(dotfiles_zsh=dotfiles_zsh, env=env)
