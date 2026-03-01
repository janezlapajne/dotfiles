from pathlib import Path

from cli import log
from cli.runner import run
from modules.base import DotfileModule


class TmuxModule(DotfileModule):
    name = "tmux"

    def install(self) -> None:
        tmux_dir = Path.home() / ".tmux"
        if tmux_dir.is_dir():
            log.info("Updating .tmux")
            run(["git", "pull"], cwd=tmux_dir)
        else:
            log.info("Cloning .tmux")
            run(
                [
                    "git",
                    "clone",
                    "--depth=1",
                    "https://github.com/gpakosz/.tmux.git",
                    str(tmux_dir),
                ]
            )

        tmux_module_dir = self.config.dotfiles_root / "tmux"
        # Copy config files from cloned repo to dotfiles module
        (tmux_module_dir / "tmux.conf.local").write_text(
            (tmux_dir / ".tmux.conf.local").read_text()
        )
        (tmux_module_dir / ".tmux.conf").write_text((tmux_dir / ".tmux.conf").read_text())

    def setup(self) -> None:
        tmux_module_dir = self.config.dotfiles_root / "tmux"
        local_conf = tmux_module_dir / ".tmux.conf.local"
        if local_conf.exists():
            log.warn(
                f"Local tmux already setup. Delete {local_conf} and run setup again to overwrite."
            )
            return

        log.info("Setup tmux config")
        source = tmux_module_dir / "tmux.conf.local"
        if source.exists():
            local_conf.write_text(source.read_text())
            log.success("Setup complete")
        else:
            log.warn("tmux.conf.local source not found — run install first.")
