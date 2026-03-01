from pathlib import Path

from cli.runner import run
from modules.base import DotfileModule


class ZshModule(DotfileModule):
    name = "zsh"

    def install(self) -> None:
        oh_my_zsh = Path.home() / ".oh-my-zsh"
        if not oh_my_zsh.is_dir():
            run(
                'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"',
                shell=True,
            )
        else:
            run(
                ["zsh", "-c", "source $HOME/.oh-my-zsh/oh-my-zsh.sh && omz update"],
            )

        if self.env("TERMINAL_THEME_STARSHIP") == "true":
            run(
                "curl -sS https://starship.rs/install.sh | sh -s -- -y",
                shell=True,
            )
