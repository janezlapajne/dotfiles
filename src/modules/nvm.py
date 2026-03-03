from cli.runner import run
from modules.base import DotfileModule


class NvmModule(DotfileModule):
    def install(self) -> None:
        run(
            "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash",
            shell=True,
        )
