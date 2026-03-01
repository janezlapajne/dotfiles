from __future__ import annotations

from pathlib import Path

import pytest

from cli.config import Config, OperatingSystem
from cli.env import update_env


class TestUpdateEnv:
    def _make_config(self, tmp_path: Path) -> Config:
        dotfiles_zsh = tmp_path / ".dotfiles"
        dotfiles_zsh.mkdir()
        return Config(
            dotfiles_zsh=dotfiles_zsh,
            home=tmp_path / "home",
            os=OperatingSystem.MACOS,
            env={},
        )

    def test_generates_example_with_stripped_values(self, tmp_path: Path):
        config = self._make_config(tmp_path)
        env_file = config.dotfiles_zsh / ".env"
        env_file.write_text("GIT_NAME=John Doe\nGIT_EMAIL=john@example.com\n")

        update_env(config)

        example = (config.dotfiles_zsh / ".env.example").read_text()
        assert "GIT_NAME=" in example
        assert "GIT_EMAIL=" in example
        assert "John Doe" not in example
        assert "john@example.com" not in example

    def test_preserves_comments(self, tmp_path: Path):
        config = self._make_config(tmp_path)
        env_file = config.dotfiles_zsh / ".env"
        env_file.write_text("# Git settings\nGIT_NAME=John\n")

        update_env(config)

        example = (config.dotfiles_zsh / ".env.example").read_text()
        assert "# Git settings" in example

    def test_preserves_empty_lines(self, tmp_path: Path):
        config = self._make_config(tmp_path)
        env_file = config.dotfiles_zsh / ".env"
        env_file.write_text("A=1\n\nB=2\n")

        update_env(config)

        example = (config.dotfiles_zsh / ".env.example").read_text()
        lines = example.splitlines()
        # After header, should contain: "", "A=", "", "B="
        content_lines = [l for l in lines if not l.startswith("#")]
        assert "" in content_lines

    def test_includes_header(self, tmp_path: Path):
        config = self._make_config(tmp_path)
        (config.dotfiles_zsh / ".env").write_text("KEY=val\n")

        update_env(config)

        example = (config.dotfiles_zsh / ".env.example").read_text()
        assert "Example .env file" in example
        assert "tail -n +7" in example

    def test_missing_env_file_calls_fail(self, tmp_path: Path):
        config = self._make_config(tmp_path)
        # No .env file created
        with pytest.raises(SystemExit):
            update_env(config)
