from cli import log
from cli.config import GITCONFIG_LOCAL, GITCONFIG_LOCAL_EXAMPLE
from modules.base import DotfileModule


class GitModule(DotfileModule):
    def setup(self) -> None:
        local_config = self.config.git_module_dir / GITCONFIG_LOCAL
        if local_config.exists():
            log.warn(
                f"Gitconfig already setup. Delete {local_config} and run setup again to overwrite."
            )
            return

        log.info("Setup gitconfig")
        example = self.config.git_module_dir / GITCONFIG_LOCAL_EXAMPLE
        content = example.read_text()
        content = content.replace("USER_NAME", self.env("GIT_NAME"))
        content = content.replace("USER_EMAIL", self.env("GIT_EMAIL"))
        content = content.replace("CREDENTIAL_HELPER", self.env("GIT_CREDENTIAL_HELPER"))
        local_config.write_text(content)
        log.success("Gitconfig setup complete")
