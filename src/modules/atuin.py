from cli import log
from cli.runner import command_exists, run
from modules.base import DotfileModule


class AtuinModule(DotfileModule):
    name = "atuin"

    def install(self) -> None:
        if command_exists("atuin"):
            log.info("Atuin already installed")
        else:
            run(
                "bash <(curl --proto '=https' --tlsv1.2 -sSf https://setup.atuin.sh)",
                shell=True,
            )

    def setup(self) -> None:
        username = self.env("ATUIN_USERNAME")
        email = self.env("ATUIN_EMAIL")
        password = self.env("ATUIN_PASSWORD")
        key = self.env("ATUIN_KEY")

        # Register to sync server
        if username and email and password and not key:
            log.info("Registering to sync server...")
            run(["atuin", "register", "-u", username, "-e", email, "-p", password])
            run(["atuin", "import", "auto"])
            run(["atuin", "sync"])
            log.success("Registration and sync successful.")
        elif key:
            log.info("Key found. Skipping registration.")
        else:
            log.fail(
                "Registration failed. Please ensure ATUIN_USERNAME, ATUIN_EMAIL, and ATUIN_PASSWORD are set."
            )

        # Login to sync server
        if username and password and key:
            log.info("Logging in to sync server...")
            run(["atuin", "login", "-u", username, "-p", password, "-k", key])
            run(["atuin", "sync"])
            log.success("Login and sync successful.")
        else:
            log.warn(
                "Login not successful. Please ensure ATUIN_USERNAME, ATUIN_PASSWORD, and ATUIN_KEY are set."
            )
