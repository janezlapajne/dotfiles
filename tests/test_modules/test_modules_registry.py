from __future__ import annotations

from cli.config import Config
from modules import get_all_modules
from modules.base import DotfileModule
from modules.zsh import ZshModule


class TestModuleRegistry:
    def test_returns_all_modules(self, macos_config: Config):
        modules = get_all_modules(macos_config)
        assert len(modules) == 9

    def test_all_are_dotfile_modules(self, macos_config: Config):
        modules = get_all_modules(macos_config)
        for module in modules:
            assert isinstance(module, DotfileModule)

    def test_zsh_is_first(self, macos_config: Config):
        modules = get_all_modules(macos_config)
        assert isinstance(modules[0], ZshModule)

    def test_all_have_unique_names(self, macos_config: Config):
        modules = get_all_modules(macos_config)
        names = [m.name for m in modules]
        assert len(names) == len(set(names))

    def test_expected_module_names(self, macos_config: Config):
        modules = get_all_modules(macos_config)
        names = {m.name for m in modules}
        expected = {"zsh", "atuin", "docker", "gh", "git", "nvm", "ssh", "tmux", "vim"}
        assert names == expected

    def test_all_receive_config(self, macos_config: Config):
        modules = get_all_modules(macos_config)
        for module in modules:
            assert module.config is macos_config
