from pathlib import Path
from unittest.mock import patch

from cli.config import Config
from modules.tmux import TmuxModule


class TestTmuxInstall:
    def test_clones_if_not_exists(self, macos_config: Config, mocker):
        mock_run = mocker.patch("modules.tmux.run")
        fake_home = macos_config.home
        fake_home.mkdir(parents=True, exist_ok=True)

        # Setup module dir for the copy step
        tmux_mod = macos_config.dotfiles_root / "tmux"
        tmux_mod.mkdir(parents=True)

        # The clone creates .tmux dir, so we need to simulate that
        tmux_dir = fake_home / ".tmux"

        def side_effect(cmd, **kwargs):
            if cmd[0] == "git" and cmd[1] == "clone":
                tmux_dir.mkdir()
                (tmux_dir / ".tmux.conf.local").write_text("local config")
                (tmux_dir / ".tmux.conf").write_text("main config")

        mock_run.side_effect = side_effect

        with patch("modules.tmux.Path.home", return_value=fake_home):
            module = TmuxModule(macos_config)
            module.install()

        # Should have called git clone
        cmds = [call.args[0] for call in mock_run.call_args_list]
        assert any("clone" in str(c) for c in cmds)

    def test_pulls_if_exists(self, macos_config: Config, mocker):
        mock_run = mocker.patch("modules.tmux.run")
        fake_home = macos_config.home
        fake_home.mkdir(parents=True, exist_ok=True)
        tmux_dir = fake_home / ".tmux"
        tmux_dir.mkdir()
        (tmux_dir / ".tmux.conf.local").write_text("local")
        (tmux_dir / ".tmux.conf").write_text("main")

        tmux_mod = macos_config.dotfiles_root / "tmux"
        tmux_mod.mkdir(parents=True)

        with patch("modules.tmux.Path.home", return_value=fake_home):
            module = TmuxModule(macos_config)
            module.install()

        cmds = [call.args[0] for call in mock_run.call_args_list]
        assert any("pull" in str(c) for c in cmds)


class TestTmuxSetup:
    def test_copies_template(self, macos_config: Config, mocker):
        mocker.patch("modules.tmux.log")
        tmux_mod = macos_config.dotfiles_root / "tmux"
        tmux_mod.mkdir(parents=True)
        (tmux_mod / "tmux.conf.local").write_text("template content")

        module = TmuxModule(macos_config)
        module.setup()

        assert (tmux_mod / ".tmux.conf.local").read_text() == "template content"

    def test_skips_if_already_exists(self, macos_config: Config, mocker):
        mocker.patch("modules.tmux.log")
        tmux_mod = macos_config.dotfiles_root / "tmux"
        tmux_mod.mkdir(parents=True)
        (tmux_mod / ".tmux.conf.local").write_text("existing")
        (tmux_mod / "tmux.conf.local").write_text("template")

        module = TmuxModule(macos_config)
        module.setup()

        assert (tmux_mod / ".tmux.conf.local").read_text() == "existing"
