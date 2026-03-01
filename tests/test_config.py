from pathlib import Path
from unittest.mock import patch

import pytest
from dotenv import dotenv_values

from cli.config import Config


class TestLoadEnv:
    def test_basic_key_value(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("FOO=bar\nBAZ=qux\n")
        result = {k: v for k, v in dotenv_values(env_file).items() if v}
        assert result == {"FOO": "bar", "BAZ": "qux"}

    def test_comments_ignored(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("# comment\nFOO=bar\n")
        result = {k: v for k, v in dotenv_values(env_file).items() if v}
        assert result == {"FOO": "bar"}

    def test_empty_lines_ignored(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("FOO=bar\n\nBAZ=qux\n")
        result = {k: v for k, v in dotenv_values(env_file).items() if v}
        assert result == {"FOO": "bar", "BAZ": "qux"}

    def test_empty_value_excluded(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("FOO=\nBAR=value\n")
        result = {k: v for k, v in dotenv_values(env_file).items() if v}
        assert result == {"BAR": "value"}

    def test_value_with_equals(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("URL=https://example.com?a=1&b=2\n")
        result = {k: v for k, v in dotenv_values(env_file).items() if v}
        assert result == {"URL": "https://example.com?a=1&b=2"}

    def test_nonexistent_file_returns_empty(self, tmp_path: Path):
        result = {k: v for k, v in dotenv_values(tmp_path / "nonexistent").items() if v}
        assert result == {}

    def test_empty_file(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("")
        result = {k: v for k, v in dotenv_values(env_file).items() if v}
        assert result == {}


class TestConfig:
    def test_dotfiles_root_property(self, macos_config: Config):
        assert macos_config.dotfiles_root == macos_config.dotfiles_zsh / "conf" / "dotfiles"

    def test_frozen_immutable(self, macos_config: Config):
        with pytest.raises(AttributeError):
            macos_config.home = Path("/other")  # type: ignore[misc]

    def test_load_reads_env(self, tmp_path: Path):
        dotfiles_dir = tmp_path / ".dotfiles"
        dotfiles_dir.mkdir()
        (dotfiles_dir / ".env").write_text("KEY=value\n")
        with patch("cli.config.Path.home", return_value=tmp_path):
            config = Config.load()
        assert config.env == {"KEY": "value"}

    def test_load_missing_env_returns_empty(self, tmp_path: Path):
        dotfiles_dir = tmp_path / ".dotfiles"
        dotfiles_dir.mkdir()
        with patch("cli.config.Path.home", return_value=tmp_path):
            config = Config.load()
        assert config.env == {}

    def test_env_dict_accessible(self, macos_config: Config):
        assert macos_config.env["GIT_NAME"] == "Test User"
        assert macos_config.env["GIT_EMAIL"] == "test@example.com"
