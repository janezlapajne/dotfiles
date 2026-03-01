from __future__ import annotations

from pathlib import Path

from cli import log
from cli.config import Config, OperatingSystem
from cli.runner import run


def install_tools(config: Config) -> None:
    log.info("Installing tools")

    if config.os == OperatingSystem.MACOS:
        log.info("Detected macOS — no additional tools to install")
        return

    log.info("Detected Linux/WSL — installing additional tools")

    # bat
    run(["sudo", "apt", "install", "-y", "bat"])
    bat_link = Path.home() / ".local" / "bin" / "bat"
    if not bat_link.exists():
        run("ln -s $(which batcat) ~/.local/bin/bat", shell=True)
    else:
        log.warn("Symbolic link ~/.local/bin/bat already exists.")

    # fd-find
    run(["sudo", "apt", "install", "-y", "fd-find"])
    fd_link = Path.home() / ".local" / "bin" / "fd"
    if not fd_link.exists():
        run("ln -s $(which fdfind) ~/.local/bin/fd", shell=True)
    else:
        log.warn("Symbolic link ~/.local/bin/fd already exists.")

    # fkill
    run(["npm", "install", "--global", "fkill-cli"])

    # pdm
    run(
        "curl -sSL https://pdm-project.org/install-pdm.py | python3 -",
        shell=True,
    )

    # tldr
    run(["pip3", "install", "tldr"])

    # zoxide
    run(
        "curl -sS https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | bash",
        shell=True,
    )

    log.success("Tools installed successfully.")
