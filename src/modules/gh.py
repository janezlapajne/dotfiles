from cli import log
from cli.runner import run
from modules.base import DotfileModule


class GhModule(DotfileModule):
    def install(self) -> None:
        # Update copilot extension if logged in
        result = run(
            ["gh", "auth", "status"],
            check=False,
            capture=True,
        )
        if result.returncode == 0:
            log.info("User is logged in. Updating copilot extension...")
            run(["gh", "extension", "upgrade", "copilot"], check=False)
        else:
            log.info("User is not logged in. Skipping copilot extension upgrade.")

    def setup(self) -> None:
        result = run(
            ["gh", "auth", "status", "-h", "github.com"],
            check=False,
            capture=True,
        )
        if result.returncode != 0:
            log.info("Not logged in to GitHub, starting login process...")
            run(["gh", "auth", "login", "--web", "-h", "github.com"])
            run(["gh", "extension", "install", "github/gh-copilot"])
            run(["gh", "extension", "install", "dlvhdr/gh-dash"])
            run(["gh", "extension", "install", "https://github.com/nektos/gh-act"])
            log.success("Successfully logged in to GitHub.")
        else:
            log.info("Already logged in to GitHub.")
