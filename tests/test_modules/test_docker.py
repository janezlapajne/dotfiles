from cli.config import Config
from modules.docker import DockerModule


class TestDockerModule:
    def test_has_name(self, macos_config: Config):
        module = DockerModule(macos_config)
        assert module.name == "docker"
