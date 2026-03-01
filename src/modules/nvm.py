from __future__ import annotations

from cli.runner import run
from modules.base import DotfileModule


class NvmModule(DotfileModule):
    name = "nvm"

    def install(self) -> None:
        run(
            "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash",
            shell=True,
        )
