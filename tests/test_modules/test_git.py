from __future__ import annotations

from pathlib import Path

import pytest

from cli.config import Config, OperatingSystem
from modules.git import GitModule


class TestGitModuleInstall:
    def test_skips_on_macos(self, macos_config: Config, mocker):
        mock_run = mocker.patch("modules.git.run")
        module = GitModule(macos_config)
        module.install()
        mock_run.assert_not_called()

    def test_installs_lazygit_on_linux(self, linux_config: Config, mocker):
        mock_run = mocker.patch("modules.git.run")
        module = GitModule(linux_config)
        module.install()
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[1]["shell"] is True
        assert "lazygit" in call_args[0][0]


class TestGitModuleSetup:
    def test_generates_gitconfig_local(self, macos_config: Config, mocker):
        mocker.patch("modules.git.log")
        git_dir = macos_config.dotfiles_root / "git"
        git_dir.mkdir(parents=True)
        (git_dir / ".gitconfig.local.example").write_text(
            "[user]\n  name = USER_NAME\n  email = USER_EMAIL\n"
            "[credential]\n  helper = CREDENTIAL_HELPER\n"
        )

        module = GitModule(macos_config)
        module.setup()

        result = (git_dir / ".gitconfig.local").read_text()
        assert "Test User" in result
        assert "test@example.com" in result
        assert "osxkeychain" in result
        assert "USER_NAME" not in result
        assert "USER_EMAIL" not in result
        assert "CREDENTIAL_HELPER" not in result

    def test_skips_if_already_exists(self, macos_config: Config, mocker):
        mocker.patch("modules.git.log")
        git_dir = macos_config.dotfiles_root / "git"
        git_dir.mkdir(parents=True)
        existing = git_dir / ".gitconfig.local"
        existing.write_text("existing content")
        (git_dir / ".gitconfig.local.example").write_text("template")

        module = GitModule(macos_config)
        module.setup()

        # Should not overwrite
        assert existing.read_text() == "existing content"
