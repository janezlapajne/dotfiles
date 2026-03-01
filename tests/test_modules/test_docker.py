from __future__ import annotations

from cli.config import Config
from modules.docker import DockerModule


class TestDockerInstall:
    def test_skips_on_macos(self, macos_config: Config, mocker):
        mock_run = mocker.patch("modules.docker.run")
        module = DockerModule(macos_config)
        module.install()
        mock_run.assert_not_called()

    def test_installs_on_linux(self, linux_config: Config, mocker):
        mock_run = mocker.patch("modules.docker.run")
        module = DockerModule(linux_config)
        module.install()
        mock_run.assert_called_once()
        assert "lazydocker" in mock_run.call_args[0][0]
