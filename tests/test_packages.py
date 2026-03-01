from cli.config import Config
from cli.packages import (
    MACOS_CASKS,
    MACOS_PACKAGES,
    install_packages,
)


class TestPackageLists:
    def test_macos_packages_not_empty(self):
        assert len(MACOS_PACKAGES) > 0

    def test_macos_casks_not_empty(self):
        assert len(MACOS_CASKS) > 0

    def test_macos_packages_contains_essentials(self):
        for pkg in ["git", "vim", "zsh", "tmux", "curl", "fzf", "ripgrep"]:
            assert pkg in MACOS_PACKAGES, f"Missing essential macOS package: {pkg}"

    def test_macos_has_brew_specific_packages(self):
        for pkg in ["gh", "uv", "eza", "bat", "fd", "lazygit"]:
            assert pkg in MACOS_PACKAGES

    def test_no_duplicate_packages(self):
        assert len(MACOS_PACKAGES) == len(set(MACOS_PACKAGES))
        assert len(MACOS_CASKS) == len(set(MACOS_CASKS))


class TestInstallPackages:
    def test_macos_uses_brew(self, macos_config: Config, mocker):
        mock_run = mocker.patch("cli.packages.run")
        mocker.patch("cli.packages.command_exists", return_value=True)

        install_packages(macos_config)

        # Should call brew update, upgrade, then install packages
        cmds = [call.args[0] for call in mock_run.call_args_list]
        assert ["brew", "update"] in cmds
        assert ["brew", "upgrade"] in cmds
        # Check at least one package install
        assert any(
            c == ["brew", "install", pkg]
            for c in cmds
            for pkg in MACOS_PACKAGES
        )

    def test_macos_installs_homebrew_if_missing(self, macos_config: Config, mocker):
        mock_run = mocker.patch("cli.packages.run")
        mocker.patch("cli.packages.command_exists", return_value=False)

        install_packages(macos_config)

        # First run call should be the Homebrew install
        first_call = mock_run.call_args_list[0]
        assert "Homebrew" in str(first_call)

    def test_macos_installs_casks(self, macos_config: Config, mocker):
        mock_run = mocker.patch("cli.packages.run")
        mocker.patch("cli.packages.command_exists", return_value=True)

        install_packages(macos_config)

        cmds = [call.args[0] for call in mock_run.call_args_list]
        for cask in MACOS_CASKS:
            assert ["brew", "install", "--cask", cask] in cmds
