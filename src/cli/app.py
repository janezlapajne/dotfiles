import os
import subprocess

import typer

from cli import log
from cli.config import DEFAULT_EDITOR, Config
from cli.env import update_env
from cli.packages import install_packages
from cli.runner import run
from cli.symlinks import setup_dotfiles
from modules import get_all_modules


def main(
    edit: bool = typer.Option(False, "-e", "--edit", help="Open dotfiles directory for editing"),
    setup: bool = typer.Option(False, "--setup", help="Full bootstrap: install, setup, symlink"),
    symlink_only: bool = typer.Option(False, "--symlink-only", help="Only create dotfile symlinks"),
    env_update: bool = typer.Option(
        False, "--env-update", help="Regenerate .env.example from .env"
    ),
) -> None:
    """Dotfiles management CLI."""
    config = Config.load()

    if edit:
        editor = os.environ.get("EDITOR", DEFAULT_EDITOR)
        subprocess.run([editor, str(config.dotfiles_zsh)])
        raise typer.Exit()

    if env_update:
        update_env(config)
        raise typer.Exit()

    if setup:
        _do_setup(config)
        raise typer.Exit()

    if symlink_only:
        setup_dotfiles(config)
        log.success("Dotfiles symlinked successfully.")
        raise typer.Exit()

    # Default behavior
    _do_update(config)


def _do_setup(config: Config) -> None:
    """Full bootstrap: install packages, tools, modules, run setup, create symlinks."""
    log.info("Installing dependencies")
    install_packages(config)

    for module in get_all_modules(config):
        module.run_install()

    log.success("Dependencies installed")

    for module in get_all_modules(config):
        module.run_setup()

    log.success("Setup scripts executed successfully.")

    setup_dotfiles(config)

    log.success("Done!")


def _do_update(config: Config) -> None:
    """Maintenance: pull latest, install packages/tools/modules."""
    log.info("Updating repository...")
    result = run(["git", "pull", "--ff-only"], cwd=config.dotfiles_zsh, check=False)
    if result.returncode == 0:
        log.success("Repository updated successfully.")
    else:
        log.fail("Error updating repository. Fast-forward merge not possible.")

    install_packages(config)

    for module in get_all_modules(config):
        module.run_install()

    log.success("Installation scripts executed successfully.")


def app_main() -> None:
    typer.run(main)
