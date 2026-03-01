from __future__ import annotations

from pathlib import Path

from cli import log
from cli.config import Config

_HEADER = """\
################################################
# Example .env file
# Use command:  $ tail -n +7 .env.example > .env
# -> to create .env file from .env.example
################################################
"""


def update_env(config: Config) -> None:
    input_file = config.dotfiles_zsh / ".env"
    output_file = config.dotfiles_zsh / ".env.example"

    if not input_file.exists():
        log.fail(".env file not found. Create one from .env.example first.")
        return

    lines: list[str] = [_HEADER, ""]

    for line in input_file.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            lines.append(stripped)
        elif "=" in stripped:
            key = stripped.split("=", 1)[0]
            lines.append(f"{key}=")
        else:
            lines.append("")

    output_file.write_text("\n".join(lines) + "\n")
    log.success(f"Updated {output_file}")
