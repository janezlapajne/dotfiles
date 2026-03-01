from __future__ import annotations

from cli import log
from cli.config import Config, OperatingSystem
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

LINUX_PACKAGES: list[str] = [
    "atop",
    "curl",
    "fzf",
    "git",
    "httpie",
    "pipx",
    "python3",
    "tmux",
    "vim",
    "wget",
    "xclip",
    "zsh",
    "ripgrep",
]


def install_packages(config: Config) -> None:
    log.info("Installing packages")

    if config.os == OperatingSystem.MACOS:
        log.info("Detected macOS — using Homebrew")

        if not command_exists("brew"):
            log.info("Installing Homebrew...")
            run(
                '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
                shell=True,
            )

        run(["brew", "update"])
        run(["brew", "upgrade"])

        log.info("Installing Fira Code Nerd Font...")
        for cask in MACOS_CASKS:
            run(["brew", "install", "--cask", cask])

        for pkg in MACOS_PACKAGES:
            run(["brew", "install", pkg])

    else:
        log.info("Detected Linux/WSL — using apt-get")
        run(["sudo", "apt-get", "update"])
        run(["sudo", "apt-get", "upgrade", "-y"])

        for pkg in LINUX_PACKAGES:
            run(["sudo", "apt-get", "install", "-y", pkg])

    log.success("Packages installed successfully.")
