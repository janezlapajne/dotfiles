from __future__ import annotations

from pathlib import Path

from cli import log
from cli.runner import run
from modules.base import DotfileModule


class VimModule(DotfileModule):
    name = "vim"

    def install(self) -> None:
        vim_runtime = Path.home() / ".vim_runtime"
        if vim_runtime.is_dir():
            log.info("Updating .vim_runtime")
            run(["git", "reset", "--hard"], cwd=vim_runtime)
            run(["git", "clean", "-d", "--force"], cwd=vim_runtime)
            run(["git", "pull", "--rebase"], cwd=vim_runtime)
            run(["python3", "update_plugins.py"], cwd=vim_runtime)
        else:
            log.info("Cloning .vim_runtime")
            run(
                [
                    "git",
                    "clone",
                    "--depth=1",
                    "https://github.com/amix/vimrc.git",
                    str(vim_runtime),
                ]
            )
