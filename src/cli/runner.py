from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from cli import log


def run(
    cmd: str | list[str],
    *,
    shell: bool = False,
    cwd: Path | None = None,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    if isinstance(cmd, list):
        display = " ".join(cmd)
    else:
        display = cmd
    log.info(f"Running: {display}")
    return subprocess.run(
        cmd,
        shell=shell,
        cwd=cwd,
        check=check,
        capture_output=capture,
        text=True,
    )


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None
