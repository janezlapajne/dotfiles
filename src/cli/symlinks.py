import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

from cli import log
from cli.config import Config


@dataclass(frozen=True)
class SymlinkEntry:
    src: Path
    dst: Path


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


def _load_symlinks(config: Config) -> list[SymlinkEntry]:
    with open(config.symlinks_file, "rb") as f:
        data = tomllib.load(f)

    symlinks_section = data["symlinks"]
    dotfiles_root = config.dotfiles_root
    home = config.home
    entries: list[SymlinkEntry] = []

    for rel_src in symlinks_section.get("root", []):
        src = dotfiles_root / rel_src
        dst = home / Path(rel_src).name
        entries.append(SymlinkEntry(src=src, dst=dst))

    for rel_src, target_dir in symlinks_section.get("targets", {}).items():
        src = dotfiles_root / rel_src
        dst = home / target_dir / Path(rel_src).name
        entries.append(SymlinkEntry(src=src, dst=dst))

    return entries


def _validate_symlinks(entries: list[SymlinkEntry]) -> list[SymlinkEntry]:
    valid: list[SymlinkEntry] = []
    seen_dst: dict[Path, str] = {}

    for entry in entries:
        if not entry.src.exists():
            log.warn(f"Source does not exist, skipping: {entry.src}")
            continue

        resolved_dst = entry.dst.resolve()
        if resolved_dst in seen_dst:
            log.fail(
                f"Duplicate destination {entry.dst} "
                f"(from {entry.src} and {seen_dst[resolved_dst]})"
            )
            sys.exit(1)

        seen_dst[resolved_dst] = str(entry.src)
        valid.append(entry)

    return valid


def setup_dotfiles(config: Config) -> None:
    log.info("Installing dotfiles")

    entries = _load_symlinks(config)
    entries = _validate_symlinks(entries)

    overwrite_all = False
    backup_all = False
    skip_all = False

    for entry in entries:
        src = entry.src
        dst = entry.dst
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
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.symlink_to(src)
            log.success(f"linked {src} to {dst}")
