from pathlib import Path

import pytest

from cli.config import Config


@pytest.fixture
def macos_config(tmp_path: Path) -> Config:
    """Config pointing at a temporary directory, simulating macOS."""
    dotfiles_zsh = tmp_path / ".dotfiles"
    dotfiles_zsh.mkdir()
    (dotfiles_zsh / "conf" / "dotfiles").mkdir(parents=True)
    env_file = dotfiles_zsh / ".env"
    env_file.write_text(
        "GIT_NAME=Test User\n"
        "GIT_EMAIL=test@example.com\n"
        "GIT_CREDENTIAL_HELPER=osxkeychain\n"
        "SSH_EMAIL=test@example.com\n"
        "SSH_PASSPHRASE=secret\n"
        "ATUIN_USERNAME=testuser\n"
        "ATUIN_EMAIL=test@example.com\n"
        "ATUIN_PASSWORD=pass123\n"
        "ATUIN_KEY=mykey\n"
        "TERMINAL_THEME_STARSHIP=false\n"
    )
    return Config(
        dotfiles_zsh=dotfiles_zsh,
        home=tmp_path / "home",
        env={
            "GIT_NAME": "Test User",
            "GIT_EMAIL": "test@example.com",
            "GIT_CREDENTIAL_HELPER": "osxkeychain",
            "SSH_EMAIL": "test@example.com",
            "SSH_PASSPHRASE": "secret",
            "ATUIN_USERNAME": "testuser",
            "ATUIN_EMAIL": "test@example.com",
            "ATUIN_PASSWORD": "pass123",
            "ATUIN_KEY": "mykey",
            "TERMINAL_THEME_STARSHIP": "false",
        },
    )
