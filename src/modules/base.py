from abc import ABC, abstractmethod

from cli import log
from cli.config import Config


class DotfileModule(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    def __init__(self, config: Config) -> None:
        self.config = config

    def install(self) -> None:
        pass

    def setup(self) -> None:
        pass

    def env(self, key: str) -> str:
        return self.config.env.get(key, "")

    def run_install(self) -> None:
        log.info(f"Installing module: {self.name}")
        try:
            self.install()
            log.success(f"Module {self.name} installed successfully.")
        except Exception as e:
            log.fail(f"Error installing module {self.name}: {e}")

    def run_setup(self) -> None:
        log.info(f"Setting up module: {self.name}")
        try:
            self.setup()
            log.success(f"Module {self.name} setup complete.")
        except Exception as e:
            log.fail(f"Error setting up module {self.name}: {e}")
