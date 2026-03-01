from cli.config import Config
from modules.atuin import AtuinModule
from modules.base import DotfileModule
from modules.gh import GhModule
from modules.git import GitModule
from modules.nvm import NvmModule
from modules.ssh import SshModule
from modules.tmux import TmuxModule
from modules.vim import VimModule
from modules.zsh import ZshModule

# ZshModule first (oh-my-zsh is a dependency), then alphabetical
_MODULE_CLASSES: list[type[DotfileModule]] = [
    ZshModule,
    AtuinModule,
    GhModule,
    GitModule,
    NvmModule,
    SshModule,
    TmuxModule,
    VimModule,
]


def get_all_modules(config: Config) -> list[DotfileModule]:
    return [cls(config) for cls in _MODULE_CLASSES]
