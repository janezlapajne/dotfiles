from cli import log
from modules.base import DotfileModule


class GitModule(DotfileModule):
    def setup(self) -> None:
        local_config = self.config.dotfiles_root / "git" / ".gitconfig.local"
        if local_config.exists():
            log.warn(
                f"Gitconfig already setup. Delete {local_config} and run setup again to overwrite."
            )
            return

        log.info("Setup gitconfig")
        example = self.config.dotfiles_root / "git" / ".gitconfig.local.example"
        content = example.read_text()
        content = content.replace("USER_NAME", self.env("GIT_NAME"))
        content = content.replace("USER_EMAIL", self.env("GIT_EMAIL"))
        content = content.replace("CREDENTIAL_HELPER", self.env("GIT_CREDENTIAL_HELPER"))
        local_config.write_text(content)
        log.success("Gitconfig setup complete")
