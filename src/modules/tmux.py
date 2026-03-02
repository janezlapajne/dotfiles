from cli import log
from cli.config import TMUX_CONF, TMUX_CONF_LOCAL, TMUX_CONF_LOCAL_TEMPLATE
from cli.runner import run
from modules.base import DotfileModule


class TmuxModule(DotfileModule):
    def install(self) -> None:
        tmux_dir = self.config.tmux_dir
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

        tmux_module_dir = self.config.tmux_module_dir
        # Copy config files from cloned repo to dotfiles module
        (tmux_module_dir / TMUX_CONF_LOCAL_TEMPLATE).write_text(
            (tmux_dir / TMUX_CONF_LOCAL).read_text()
        )
        (tmux_module_dir / TMUX_CONF).write_text(
            (tmux_dir / TMUX_CONF).read_text()
        )

    def setup(self) -> None:
        tmux_module_dir = self.config.tmux_module_dir
        local_conf = tmux_module_dir / TMUX_CONF_LOCAL
        if local_conf.exists():
            log.warn(
                f"Local tmux already setup. Delete {local_conf} and run setup again to overwrite."
            )
            return

        log.info("Setup tmux config")
        source = tmux_module_dir / TMUX_CONF_LOCAL_TEMPLATE
        if source.exists():
            local_conf.write_text(source.read_text())
            log.success("Setup complete")
        else:
            log.warn("tmux.conf.local source not found — run install first.")
