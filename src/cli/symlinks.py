import sys
import termios
import tomllib
import tty
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from cli import log
from cli.config import Config


class Action(Enum):
    SKIP = "skip"
    OVERWRITE = "overwrite"
    BACKUP = "backup"


@dataclass(frozen=True)
class SymlinkEntry:
    src: Path
    dst: Path


def _read_char() -> str:
    if not sys.stdin.isatty():
        return "s"

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
                f"Duplicate destination {entry.dst} (from {entry.src} and {seen_dst[resolved_dst]})"
            )

        seen_dst[resolved_dst] = str(entry.src)
        valid.append(entry)

    return valid


def _short(path: Path, home: Path) -> str:
    """Replace the home directory prefix with ~ for display."""
    s = str(path)
    prefix = str(home)
    if s == prefix or s.startswith(prefix + "/"):
        return "~" + s[len(prefix) :]
    return s


def _prompt_action(dst: Path, src_name: str, home: Path) -> tuple[Action, bool]:
    """Prompt user for conflict resolution. Returns (action, apply_to_all)."""
    log.user(
        f"File already exists: {_short(dst, home)} ({src_name})\n"
        "       \\[s]kip, \\[S]kip all, \\[o]verwrite, \\[O]verwrite all, \\[b]ackup, \\[B]ackup all?"
    )
    key = _read_char()
    match key:
        case "o":
            return Action.OVERWRITE, False
        case "O":
            return Action.OVERWRITE, True
        case "b":
            return Action.BACKUP, False
        case "B":
            return Action.BACKUP, True
        case "S":
            return Action.SKIP, True
        case _:
            return Action.SKIP, False


def setup_dotfiles(config: Config) -> None:
    log.info("Installing dotfiles")

    entries = _load_symlinks(config)
    entries = _validate_symlinks(entries)

    home = config.home
    sticky_action: Action | None = None

    for entry in entries:
        src = entry.src
        dst = entry.dst

        if dst.exists() or dst.is_symlink():
            # Already-correct symlink: silently skip
            if dst.is_symlink() and dst.resolve() == src.resolve():
                continue

            # Determine action: use sticky or prompt
            if sticky_action is not None:
                action = sticky_action
            else:
                action, apply_all = _prompt_action(dst, src.name, home)
                if apply_all:
                    sticky_action = action

            if action is Action.SKIP:
                log.success(f"skipped {_short(dst, home)}")
                continue

            if action is Action.BACKUP:
                backup_path = dst.with_suffix(dst.suffix + ".backup")
                dst.rename(backup_path)
                log.success(f"backed up {_short(dst, home)} -> {_short(backup_path, home)}")

            if action is Action.OVERWRITE:
                if dst.is_dir() and not dst.is_symlink():
                    import shutil

                    shutil.rmtree(dst)
                else:
                    dst.unlink()
                log.success(f"removed {_short(dst, home)}")

        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.symlink_to(src)
        log.success(f"linked {_short(src, home)} -> {_short(dst, home)}")
