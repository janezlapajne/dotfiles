from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from cli.config import Config, OperatingSystem, _load_env


class TestOperatingSystem:
    def test_detect_macos(self):
        with patch("cli.config.platform.system", return_value="Darwin"):
            assert OperatingSystem.detect() == OperatingSystem.MACOS

    def test_detect_linux(self):
        with patch("cli.config.platform.system", return_value="Linux"):
            assert OperatingSystem.detect() == OperatingSystem.LINUX

    def test_detect_unknown_defaults_to_linux(self):
        with patch("cli.config.platform.system", return_value="Windows"):
            assert OperatingSystem.detect() == OperatingSystem.LINUX

    def test_enum_values(self):
        assert OperatingSystem.MACOS.value == "macos"
        assert OperatingSystem.LINUX.value == "linux"


class TestLoadEnv:
    def test_basic_key_value(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("FOO=bar\nBAZ=qux\n")
        result = _load_env(env_file)
        assert result == {"FOO": "bar", "BAZ": "qux"}

    def test_comments_ignored(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("# comment\nFOO=bar\n")
        result = _load_env(env_file)
        assert result == {"FOO": "bar"}

    def test_empty_lines_ignored(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("FOO=bar\n\nBAZ=qux\n")
        result = _load_env(env_file)
        assert result == {"FOO": "bar", "BAZ": "qux"}

    def test_empty_value_excluded(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("FOO=\nBAR=value\n")
        result = _load_env(env_file)
        assert result == {"BAR": "value"}

    def test_line_without_equals_ignored(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("NOEQUALSSIGN\nFOO=bar\n")
        result = _load_env(env_file)
        assert result == {"FOO": "bar"}

    def test_value_with_equals(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("URL=https://example.com?a=1&b=2\n")
        result = _load_env(env_file)
        assert result == {"URL": "https://example.com?a=1&b=2"}

    def test_whitespace_stripped(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("  FOO  =  bar  \n")
        result = _load_env(env_file)
        assert result == {"FOO": "bar"}

    def test_nonexistent_file_returns_empty(self, tmp_path: Path):
        result = _load_env(tmp_path / "nonexistent")
        assert result == {}

    def test_empty_file(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("")
        result = _load_env(env_file)
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
