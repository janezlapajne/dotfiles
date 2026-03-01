from __future__ import annotations

import sys
from pathlib import Path

from cli import log
from cli.config import Config

_EXCLUDED_SUFFIXES = {".zsh", ".sh", ".example"}


def _read_char() -> str:
    if not sys.stdin.isatty():
        return "s"
    import termios
    import tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    print()
    return ch


def _find_dotfiles(dotfiles_root: Path) -> list[Path]:
    results: list[Path] = []
    for child in sorted(dotfiles_root.iterdir()):
        if not child.is_dir():
            continue
        # Depth 1: direct dotfiles in module dirs
        for item in sorted(child.iterdir()):
            if item.name.startswith(".") and item.suffix not in _EXCLUDED_SUFFIXES:
                results.append(item)
            # Depth 2: nested dirs (e.g. .ssh/config)
            if item.is_dir() and not item.name.startswith("."):
                for nested in sorted(item.iterdir()):
                    if (
                        nested.name.startswith(".")
                        and nested.suffix not in _EXCLUDED_SUFFIXES
                    ):
                        results.append(nested)
    return results


def setup_dotfiles(config: Config) -> None:
    log.info("Installing dotfiles")

    overwrite_all = False
    backup_all = False
    skip_all = False

    for src in _find_dotfiles(config.dotfiles_root):
        dst = config.home / src.name
        log.info(f"{src} -> {dst}")

        overwrite = False
        backup = False
        skip = False

        if dst.exists() or dst.is_symlink():
            if not overwrite_all and not backup_all and not skip_all:
                current_target = None
                if dst.is_symlink():
                    current_target = dst.resolve()
                if current_target == src.resolve():
                    skip = True
                else:
                    log.user(
                        f"File already exists: {dst} ({src.name}), what do you want to do?\n"
                        "        [s]kip, [S]kip all, [o]verwrite, [O]verwrite all, [b]ackup, [B]ackup all?"
                    )
                    action = _read_char()
                    match action:
                        case "o":
                            overwrite = True
                        case "O":
                            overwrite_all = True
                        case "b":
                            backup = True
                        case "B":
                            backup_all = True
                        case "s":
                            skip = True
                        case "S":
                            skip_all = True

            overwrite = overwrite or overwrite_all
            backup = backup or backup_all
            skip = skip or skip_all

            if overwrite:
                if dst.is_dir() and not dst.is_symlink():
                    import shutil

                    shutil.rmtree(dst)
                else:
                    dst.unlink()
                log.success(f"removed {dst}")

            if backup:
                dst.rename(dst.with_suffix(dst.suffix + ".backup"))
                log.success(f"moved {dst} to {dst}.backup")

            if skip:
                log.success(f"skipped {src}")

        if not skip:
            dst.symlink_to(src)
            log.success(f"linked {src} to {dst}")
