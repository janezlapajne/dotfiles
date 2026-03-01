import pytest

from cli.config import Config
from modules.atuin import AtuinModule


class TestAtuinInstall:
    def test_skips_if_already_installed(self, macos_config: Config, mocker):
        mocker.patch("modules.atuin.command_exists", return_value=True)
        mock_run = mocker.patch("modules.atuin.run")

        module = AtuinModule(macos_config)
        module.install()

        mock_run.assert_not_called()

    def test_installs_if_not_found(self, macos_config: Config, mocker):
        mocker.patch("modules.atuin.command_exists", return_value=False)
        mock_run = mocker.patch("modules.atuin.run")

        module = AtuinModule(macos_config)
        module.install()

        mock_run.assert_called_once()
        assert mock_run.call_args[1]["shell"] is True


class TestAtuinSetup:
    def test_login_with_key(self, macos_config: Config, mocker):
        mock_run = mocker.patch("modules.atuin.run")
        mocker.patch("modules.atuin.log")

        module = AtuinModule(macos_config)
        module.setup()

        # With ATUIN_KEY set, should skip registration and login
        cmds = [call.args[0] for call in mock_run.call_args_list]
        assert any("login" in str(c) for c in cmds)

    def test_register_without_key(self, tmp_path, mocker):
        mock_run = mocker.patch("modules.atuin.run")
        mocker.patch("modules.atuin.log")

        config = Config(
            dotfiles_zsh=tmp_path,
            home=tmp_path / "home",
            env={
                "ATUIN_USERNAME": "user",
                "ATUIN_EMAIL": "user@test.com",
                "ATUIN_PASSWORD": "pass",
            },
        )
        module = AtuinModule(config)
        module.setup()

        cmds = [call.args[0] for call in mock_run.call_args_list]
        assert any("register" in str(c) for c in cmds)
        assert any("import" in str(c) for c in cmds)
        assert any("sync" in str(c) for c in cmds)

    def test_fails_with_no_credentials(self, tmp_path, mocker):
        mocker.patch("modules.atuin.run")
        mock_log = mocker.patch("modules.atuin.log")

        config = Config(
            dotfiles_zsh=tmp_path,
            home=tmp_path / "home",
            env={},
        )
        module = AtuinModule(config)
        module.setup()

        # Should call log.fail when no credentials are set
        mock_log.fail.assert_called_once()
