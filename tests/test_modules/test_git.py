from cli.config import Config
from modules.git import GitModule


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
