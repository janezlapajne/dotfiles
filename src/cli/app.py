from __future__ import annotations

import os
import subprocess

import typer

from cli import log
from cli.config import Config
from cli.env import update_env as _update_env
from cli.packages import install_packages
from cli.runner import run
from cli.symlinks import setup_dotfiles
from modules import get_all_modules

app = typer.Typer(help="Dotfiles management CLI")


@app.command()
def setup() -> None:
    """Full bootstrap: install packages, tools, modules, run setup, create symlinks."""
    config = Config.load()

    log.info("Installing dependencies")
    install_packages(config)

    for module in get_all_modules(config):
        module.run_install()

    log.success("Dependencies installed")

    for module in get_all_modules(config):
        module.run_setup()

    log.success("Setup scripts executed successfully.")

    setup_dotfiles(config)

    print()
    print("  Done!")


@app.command()
def dot(
    edit: bool = typer.Option(False, "-e", "--edit", help="Open dotfiles directory for editing"),
) -> None:
    """Maintenance: pull latest, install packages/tools/modules."""
    config = Config.load()

    if edit:
        editor = os.environ.get("EDITOR", "vim")
        subprocess.run([editor, str(config.dotfiles_zsh)])
        raise typer.Exit()

    # Update repository
    log.info("Updating repository...")
    result = run(["git", "pull", "--ff-only"], cwd=config.dotfiles_zsh, check=False)
    if result.returncode == 0:
        log.success("Repository updated successfully.")
    else:
        log.fail("Error updating repository. Fast-forward merge not possible.")

    # Install packages
    install_packages(config)

    # Install modules
    for module in get_all_modules(config):
        module.run_install()

    log.success("Installation scripts executed successfully.")


@app.command(name="update-env")
def update_env_cmd() -> None:
    """Regenerate .env.example from .env."""
    config = Config.load()
    _update_env(config)


def app_main() -> None:
    app()


def dot_main() -> None:
    """Entry point for the `dot` shortcut command."""
    # Simulate calling `dotfiles dot` with sys.argv forwarded
    import sys

    sys.argv = ["dotfiles", "dot"] + sys.argv[1:]
    app()
