import tomllib

from cli import log
from cli.config import Config
from cli.runner import command_exists, run


def install_packages(config: Config) -> None:
    log.info("Installing packages")

    packages_toml = config.dotfiles_zsh / "conf" / "packages.toml"
    with open(packages_toml, "rb") as f:
        pkg_config = tomllib.load(f)

    brew_packages: list[str] = pkg_config["brew"]["packages"]
    brew_casks: list[str] = pkg_config["brew"]["casks"]

    if not command_exists("brew"):
        log.info("Installing Homebrew...")
        run(
            '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            shell=True,
        )

    run(["brew", "update"])
    run(["brew", "upgrade"])

    for cask in brew_casks:
        run(["brew", "install", "--cask", cask])

    for pkg in brew_packages:
        run(["brew", "install", pkg])

    log.success("Packages installed successfully.")
