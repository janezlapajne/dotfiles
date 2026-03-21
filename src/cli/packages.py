import tomllib

from cli import log
from cli.config import Config
from cli.runner import command_exists, run


def _install_brew_packages(pkg_config: dict) -> None:
    brew_packages: list[str] = pkg_config["brew"]["packages"]
    brew_casks: list[str] = pkg_config["brew"]["casks"]

    if not command_exists("brew"):
        log.info("Installing Homebrew...")
        run(
            '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            shell=True,
        )

    run(["brew", "update"])
    run(["brew", "upgrade"], check=False)

    for cask in brew_casks:
        run(["brew", "install", "--cask", cask])

    for pkg in brew_packages:
        run(["brew", "install", pkg])


def _install_npm_packages(pkg_config: dict) -> None:
    if "npm" not in pkg_config:
        return

    npm_packages: list[str] = pkg_config["npm"]["packages"]

    if not command_exists("npm"):
        log.warn("npm not found, skipping npm packages.")
        return

    for pkg in npm_packages:
        run(["npm", "install", "--global", pkg])


def install_packages(config: Config) -> None:
    log.info("Installing packages")

    with open(config.packages_file, "rb") as f:
        pkg_config = tomllib.load(f)

    _install_brew_packages(pkg_config)
    _install_npm_packages(pkg_config)

    log.success("Packages installed successfully.")
