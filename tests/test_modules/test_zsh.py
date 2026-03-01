from pathlib import Path
from unittest.mock import patch

from cli.config import Config
from modules.zsh import ZshModule


class TestZshInstall:
    def test_installs_ohmyzsh_if_not_present(self, macos_config: Config, mocker):
        mock_run = mocker.patch("modules.zsh.run")
        fake_home = macos_config.home
        fake_home.mkdir(parents=True, exist_ok=True)

        with patch("modules.zsh.Path.home", return_value=fake_home):
            module = ZshModule(macos_config)
            module.install()

        # Should call the oh-my-zsh install script
        call_args = mock_run.call_args_list[0]
        assert "ohmyzsh" in call_args[0][0]
        assert call_args[1]["shell"] is True

    def test_updates_ohmyzsh_if_present(self, macos_config: Config, mocker):
        mock_run = mocker.patch("modules.zsh.run")
        fake_home = macos_config.home
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".oh-my-zsh").mkdir()

        with patch("modules.zsh.Path.home", return_value=fake_home):
            module = ZshModule(macos_config)
            module.install()

        cmd = mock_run.call_args_list[0][0][0]
        assert "omz update" in " ".join(cmd)

    def test_installs_starship_when_enabled(self, tmp_path, mocker):
        mock_run = mocker.patch("modules.zsh.run")
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        (fake_home / ".oh-my-zsh").mkdir()

        config = Config(
            dotfiles_zsh=tmp_path,
            home=fake_home,
            env={"TERMINAL_THEME_STARSHIP": "true"},
        )

        with patch("modules.zsh.Path.home", return_value=fake_home):
            module = ZshModule(config)
            module.install()

        # Should have two calls: omz update + starship install
        assert mock_run.call_count == 2
        starship_call = mock_run.call_args_list[1]
        assert "starship" in starship_call[0][0]

    def test_skips_starship_when_disabled(self, macos_config: Config, mocker):
        mock_run = mocker.patch("modules.zsh.run")
        fake_home = macos_config.home
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".oh-my-zsh").mkdir()

        with patch("modules.zsh.Path.home", return_value=fake_home):
            module = ZshModule(macos_config)
            module.install()

        # Only omz update, no starship
        assert mock_run.call_count == 1
