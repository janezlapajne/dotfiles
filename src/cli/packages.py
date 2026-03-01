from __future__ import annotations

from cli import log
from cli.config import Config
from cli.runner import command_exists, run

MACOS_PACKAGES: list[str] = [
    "curl",
    "fzf",
    "git",
    "gh",
    "copilot-cli",
    "httpie",
    "pipx",
    "python3",
    "tmux",
    "vim",
    "wget",
    "zsh",
    "ripgrep",
    "htop",
    "tlrc",
    "zoxide",
    "bat",
    "fd",
    "pdm",
    "uv",
    "jq",
    "lazydocker",
    "lazygit",
    "yazi",
    "ffmpeg",
    "p7zip",
    "poppler",
    "resvg",
    "imagemagick",
    "eza",
    "navi",
]

MACOS_CASKS: list[str] = [
    "font-fira-code-nerd-font",
]


def install_packages(config: Config) -> None:
    log.info("Installing packages")

    if not command_exists("brew"):
        log.info("Installing Homebrew...")
        run(
            '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            shell=True,
        )

    run(["brew", "update"])
    run(["brew", "upgrade"])

    for cask in MACOS_CASKS:
        run(["brew", "install", "--cask", cask])

    for pkg in MACOS_PACKAGES:
        run(["brew", "install", pkg])

    log.success("Packages installed successfully.")
