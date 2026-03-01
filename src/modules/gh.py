from __future__ import annotations

from cli import log
from cli.config import OperatingSystem
from cli.runner import run
from modules.base import DotfileModule


class GhModule(DotfileModule):
    name = "gh"

    def install(self) -> None:
        if self.config.os != OperatingSystem.LINUX:
            log.info("Skipping GitHub CLI installation on macOS (installed via brew)")
        else:
            run(
                "sudo mkdir -p -m 755 /etc/apt/keyrings"
                " && wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg"
                " | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null"
                " && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg"
                ' && echo "deb [arch=$(dpkg --print-architecture)'
                " signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg]"
                ' https://cli.github.com/packages stable main"'
                " | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null"
                " && sudo apt update"
                " && sudo apt install gh -y",
                shell=True,
            )

        # Update copilot extension if logged in
        result = run(
            ["gh", "auth", "status"],
            check=False,
            capture=True,
        )
        if result.returncode == 0:
            log.info("User is logged in. Updating copilot extension...")
            run(["gh", "extension", "upgrade", "copilot"], check=False)
        else:
            log.info("User is not logged in. Skipping copilot extension upgrade.")

    def setup(self) -> None:
        result = run(
            ["gh", "auth", "status", "-h", "github.com"],
            check=False,
            capture=True,
        )
        if result.returncode != 0:
            log.info("Not logged in to GitHub, starting login process...")
            run(["gh", "auth", "login", "--web", "-h", "github.com"])
            run(["gh", "extension", "install", "github/gh-copilot"])
            run(["gh", "extension", "install", "dlvhdr/gh-dash"])
            run(["gh", "extension", "install", "https://github.com/nektos/gh-act"])
            log.success("Successfully logged in to GitHub.")
        else:
            log.info("Already logged in to GitHub.")
