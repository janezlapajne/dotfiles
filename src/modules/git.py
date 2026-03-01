from __future__ import annotations

from cli import log
from cli.config import OperatingSystem
from cli.runner import run
from modules.base import DotfileModule


class GitModule(DotfileModule):
    name = "git"

    def install(self) -> None:
        if self.config.os != OperatingSystem.LINUX:
            log.info("Skipping lazygit installation on macOS (installed via brew)")
            return
        run(
            'LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest"'
            ' | grep -Po \'"tag_name": "v\\K[^"]*\')'
            " && curl -Lo lazygit.tar.gz"
            ' "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"'
            " && tar xf lazygit.tar.gz lazygit"
            " && sudo install lazygit /usr/local/bin"
            " && rm lazygit.tar.gz lazygit",
            shell=True,
        )

    def setup(self) -> None:
        local_config = self.config.dotfiles_root / "git" / ".gitconfig.local"
        if local_config.exists():
            log.warn(
                "Gitconfig already setup. Delete"
                f" {local_config} and run setup again to overwrite."
            )
            return

        log.info("Setup gitconfig")
        example = self.config.dotfiles_root / "git" / ".gitconfig.local.example"
        content = example.read_text()
        content = content.replace("USER_NAME", self.env("GIT_NAME"))
        content = content.replace("USER_EMAIL", self.env("GIT_EMAIL"))
        content = content.replace("CREDENTIAL_HELPER", self.env("GIT_CREDENTIAL_HELPER"))
        local_config.write_text(content)
        log.success("Gitconfig setup complete")
