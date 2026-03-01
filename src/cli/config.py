from dataclasses import dataclass, field
from pathlib import Path

from dotenv import dotenv_values


@dataclass(frozen=True)
class Config:
    dotfiles_zsh: Path = field(default_factory=lambda: Path.home() / ".dotfiles")
    home: Path = field(default_factory=Path.home)
    env: dict[str, str] = field(default_factory=dict)

    @property
    def dotfiles_root(self) -> Path:
        return self.dotfiles_zsh / "conf" / "dotfiles"

    @classmethod
    def load(cls) -> "Config":
        dotfiles_zsh = Path.home() / ".dotfiles"
        env = {k: v for k, v in dotenv_values(dotfiles_zsh / ".env").items() if v}
        return cls(dotfiles_zsh=dotfiles_zsh, env=env)
