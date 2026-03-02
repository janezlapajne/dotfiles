from cli import log
from cli.runner import run
from modules.base import DotfileModule


class SshModule(DotfileModule):
    def setup(self) -> None:
        key_path = self.config.ssh_key_path
        if key_path.exists():
            log.warn(
                "SSH key already setup. Delete ~/.ssh/id_rsa and run setup again to overwrite."
            )
            return

        log.info("Setup ssh key")
        email = self.env("SSH_EMAIL")
        passphrase = self.env("SSH_PASSPHRASE")

        cmd = ["ssh-keygen", "-t", "rsa", "-b", "4096", "-C", email]
        if passphrase:
            cmd += ["-N", passphrase]
        cmd += ["-f", str(key_path)]

        run(cmd)
        log.success("SSH key setup successful")
