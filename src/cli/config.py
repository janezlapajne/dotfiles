from __future__ import annotations

import platform
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class OperatingSystem(Enum):
    MACOS = "macos"
    LINUX = "linux"

    @classmethod
    def detect(cls) -> OperatingSystem:
        system = platform.system()
        if system == "Darwin":
            return cls.MACOS
        return cls.LINUX


def _load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if key and value:
            env[key] = value
    return env


@dataclass(frozen=True)
class Config:
    dotfiles_zsh: Path = field(default_factory=lambda: Path.home() / ".dotfiles")
    home: Path = field(default_factory=Path.home)
    os: OperatingSystem = field(default_factory=OperatingSystem.detect)
    env: dict[str, str] = field(default_factory=dict)

    @property
    def dotfiles_root(self) -> Path:
        return self.dotfiles_zsh / "conf" / "dotfiles"

    @classmethod
    def load(cls) -> Config:
        dotfiles_zsh = Path.home() / ".dotfiles"
        env = _load_env(dotfiles_zsh / ".env")
        return cls(dotfiles_zsh=dotfiles_zsh, env=env)
