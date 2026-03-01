from __future__ import annotations

from cli import log
from cli.config import OperatingSystem
from cli.runner import run
from modules.base import DotfileModule


class DockerModule(DotfileModule):
    name = "docker"

    def install(self) -> None:
        if self.config.os != OperatingSystem.LINUX:
            log.info("Skipping lazydocker installation on macOS (installed via brew)")
            return
        run(
            "curl https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | bash",
            shell=True,
        )
