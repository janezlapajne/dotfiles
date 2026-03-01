from __future__ import annotations

import pytest

from cli.config import Config, OperatingSystem
from modules.base import DotfileModule


class ConcreteModule(DotfileModule):
    name = "test"


class FailingInstallModule(DotfileModule):
    name = "fail_install"

    def install(self) -> None:
        raise RuntimeError("install failed")


class FailingSetupModule(DotfileModule):
    name = "fail_setup"

    def setup(self) -> None:
        raise RuntimeError("setup failed")


class TestDotfileModule:
    def test_name_is_abstract(self):
        """Cannot instantiate DotfileModule without name."""
        with pytest.raises(TypeError):

            class BadModule(DotfileModule):
                pass

            BadModule(Config(os=OperatingSystem.MACOS, env={}))

    def test_concrete_module_name(self, macos_config: Config):
        module = ConcreteModule(macos_config)
        assert module.name == "test"

    def test_env_returns_value(self, macos_config: Config):
        module = ConcreteModule(macos_config)
        assert module.env("GIT_NAME") == "Test User"

    def test_env_returns_empty_for_missing_key(self, macos_config: Config):
        module = ConcreteModule(macos_config)
        assert module.env("NONEXISTENT") == ""

    def test_install_default_is_noop(self, macos_config: Config):
        module = ConcreteModule(macos_config)
        module.install()  # Should not raise

    def test_setup_default_is_noop(self, macos_config: Config):
        module = ConcreteModule(macos_config)
        module.setup()  # Should not raise

    def test_run_install_calls_install(self, macos_config: Config):
        module = ConcreteModule(macos_config)
        module.run_install()  # Should not raise

    def test_run_setup_calls_setup(self, macos_config: Config):
        module = ConcreteModule(macos_config)
        module.run_setup()  # Should not raise

    def test_run_install_handles_failure(self, macos_config: Config):
        module = FailingInstallModule(macos_config)
        # run_install calls log.fail which raises SystemExit
        with pytest.raises(SystemExit):
            module.run_install()

    def test_run_setup_handles_failure(self, macos_config: Config):
        module = FailingSetupModule(macos_config)
        with pytest.raises(SystemExit):
            module.run_setup()

    def test_config_stored(self, macos_config: Config):
        module = ConcreteModule(macos_config)
        assert module.config is macos_config
