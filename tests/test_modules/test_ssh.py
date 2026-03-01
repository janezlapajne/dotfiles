from pathlib import Path
from unittest.mock import patch

import pytest

from cli.config import Config
from modules.ssh import SshModule


class TestSshSetup:
    def test_generates_key(self, macos_config: Config, mocker):
        mock_run = mocker.patch("modules.ssh.run")
        # Patch Path.home to return a tmp dir where .ssh/id_rsa doesn't exist
        fake_home = macos_config.home
        fake_home.mkdir(parents=True, exist_ok=True)

        with patch("modules.ssh.Path.home", return_value=fake_home):
            module = SshModule(macos_config)
            module.setup()

        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "ssh-keygen" in cmd
        assert "-t" in cmd
        assert "rsa" in cmd
        assert "-b" in cmd
        assert "4096" in cmd
        assert "test@example.com" in cmd

    def test_includes_passphrase_when_set(self, macos_config: Config, mocker):
        mock_run = mocker.patch("modules.ssh.run")
        fake_home = macos_config.home
        fake_home.mkdir(parents=True, exist_ok=True)

        with patch("modules.ssh.Path.home", return_value=fake_home):
            module = SshModule(macos_config)
            module.setup()

        cmd = mock_run.call_args[0][0]
        assert "-N" in cmd
        assert "secret" in cmd

    def test_skips_if_key_exists(self, macos_config: Config, mocker):
        mock_run = mocker.patch("modules.ssh.run")
        fake_home = macos_config.home
        ssh_dir = fake_home / ".ssh"
        ssh_dir.mkdir(parents=True)
        (ssh_dir / "id_rsa").touch()

        with patch("modules.ssh.Path.home", return_value=fake_home):
            module = SshModule(macos_config)
            module.setup()

        mock_run.assert_not_called()

    def test_no_passphrase_when_empty(self, tmp_path, mocker):
        mock_run = mocker.patch("modules.ssh.run")
        config = Config(
            dotfiles_zsh=tmp_path,
            home=tmp_path / "home",
            env={"SSH_EMAIL": "test@example.com", "SSH_PASSPHRASE": ""},
        )
        fake_home = config.home
        fake_home.mkdir(parents=True, exist_ok=True)

        with patch("modules.ssh.Path.home", return_value=fake_home):
            module = SshModule(config)
            module.setup()

        cmd = mock_run.call_args[0][0]
        assert "-N" not in cmd
