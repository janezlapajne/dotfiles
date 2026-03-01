from pathlib import Path
from unittest.mock import patch

import pytest

from cli.config import Config
from cli.symlinks import _find_dotfiles, setup_dotfiles


def _make_config(tmp_path: Path) -> Config:
    dotfiles_zsh = tmp_path / "dotfiles_repo"
    dotfiles_zsh.mkdir()
    dotfiles_root = dotfiles_zsh / "conf" / "dotfiles"
    dotfiles_root.mkdir(parents=True)
    home = tmp_path / "home"
    home.mkdir()
    return Config(
        dotfiles_zsh=dotfiles_zsh,
        home=home,
        env={},
    )


class TestFindDotfiles:
    def test_finds_dotfiles_in_module_dirs(self, tmp_path: Path):
        config = _make_config(tmp_path)
        git_dir = config.dotfiles_root / "git"
        git_dir.mkdir()
        (git_dir / ".gitconfig").touch()

        result = _find_dotfiles(config.dotfiles_root)
        assert len(result) == 1
        assert result[0].name == ".gitconfig"

    def test_excludes_zsh_files(self, tmp_path: Path):
        config = _make_config(tmp_path)
        zsh_dir = config.dotfiles_root / "zsh"
        zsh_dir.mkdir()
        (zsh_dir / ".zshrc").touch()
        (zsh_dir / "config.zsh").touch()

        result = _find_dotfiles(config.dotfiles_root)
        names = [r.name for r in result]
        assert ".zshrc" in names
        assert "config.zsh" not in names

    def test_excludes_sh_files(self, tmp_path: Path):
        config = _make_config(tmp_path)
        mod_dir = config.dotfiles_root / "test"
        mod_dir.mkdir()
        (mod_dir / ".script.sh").touch()
        (mod_dir / ".config").touch()

        result = _find_dotfiles(config.dotfiles_root)
        names = [r.name for r in result]
        assert ".script.sh" not in names
        assert ".config" in names

    def test_excludes_example_files(self, tmp_path: Path):
        config = _make_config(tmp_path)
        mod_dir = config.dotfiles_root / "git"
        mod_dir.mkdir()
        (mod_dir / ".gitconfig.local.example").touch()
        (mod_dir / ".gitconfig").touch()

        result = _find_dotfiles(config.dotfiles_root)
        names = [r.name for r in result]
        assert ".gitconfig.local.example" not in names
        assert ".gitconfig" in names

    def test_ignores_non_dotfiles(self, tmp_path: Path):
        config = _make_config(tmp_path)
        mod_dir = config.dotfiles_root / "zsh"
        mod_dir.mkdir()
        (mod_dir / "config.zsh").touch()
        (mod_dir / "regular_file").touch()
        (mod_dir / ".zshrc").touch()

        result = _find_dotfiles(config.dotfiles_root)
        names = [r.name for r in result]
        assert "config.zsh" not in names
        assert "regular_file" not in names
        assert ".zshrc" in names

    def test_finds_multiple_modules(self, tmp_path: Path):
        config = _make_config(tmp_path)
        for mod_name, dotfile in [
            ("git", ".gitconfig"),
            ("vim", ".vimrc"),
            ("tmux", ".tmux.conf"),
        ]:
            mod_dir = config.dotfiles_root / mod_name
            mod_dir.mkdir()
            (mod_dir / dotfile).touch()

        result = _find_dotfiles(config.dotfiles_root)
        names = {r.name for r in result}
        assert names == {".gitconfig", ".tmux.conf", ".vimrc"}

    def test_sorted_order(self, tmp_path: Path):
        config = _make_config(tmp_path)
        for mod_name in ["zsh", "git", "atuin"]:
            mod_dir = config.dotfiles_root / mod_name
            mod_dir.mkdir()
            (mod_dir / f".{mod_name}rc").touch()

        result = _find_dotfiles(config.dotfiles_root)
        # Modules should be sorted alphabetically
        assert result[0].parent.name == "atuin"
        assert result[1].parent.name == "git"
        assert result[2].parent.name == "zsh"

    def test_empty_dotfiles_root(self, tmp_path: Path):
        config = _make_config(tmp_path)
        result = _find_dotfiles(config.dotfiles_root)
        assert result == []


class TestSetupDotfiles:
    def test_creates_symlinks(self, tmp_path: Path):
        config = _make_config(tmp_path)
        git_dir = config.dotfiles_root / "git"
        git_dir.mkdir()
        gitconfig = git_dir / ".gitconfig"
        gitconfig.write_text("[user]\nname = test")

        setup_dotfiles(config)

        link = config.home / ".gitconfig"
        assert link.is_symlink()
        assert link.resolve() == gitconfig.resolve()

    def test_creates_multiple_symlinks(self, tmp_path: Path):
        config = _make_config(tmp_path)
        for mod_name, dotfile, content in [
            ("git", ".gitconfig", "[user]"),
            ("vim", ".vimrc", "set nocompatible"),
        ]:
            mod_dir = config.dotfiles_root / mod_name
            mod_dir.mkdir()
            (mod_dir / dotfile).write_text(content)

        setup_dotfiles(config)

        assert (config.home / ".gitconfig").is_symlink()
        assert (config.home / ".vimrc").is_symlink()

    def test_skips_already_linked(self, tmp_path: Path):
        config = _make_config(tmp_path)
        git_dir = config.dotfiles_root / "git"
        git_dir.mkdir()
        gitconfig = git_dir / ".gitconfig"
        gitconfig.write_text("[user]")

        # Pre-create correct symlink
        link = config.home / ".gitconfig"
        link.symlink_to(gitconfig)

        # Should not raise or modify
        setup_dotfiles(config)
        assert link.is_symlink()
        assert link.resolve() == gitconfig.resolve()

    def test_non_tty_auto_skips_conflicts(self, tmp_path: Path):
        """When not on a TTY, _read_char returns 's' (skip)."""
        config = _make_config(tmp_path)
        git_dir = config.dotfiles_root / "git"
        git_dir.mkdir()
        (git_dir / ".gitconfig").write_text("[user]")

        # Pre-create a regular file (conflict)
        conflict = config.home / ".gitconfig"
        conflict.write_text("existing content")

        setup_dotfiles(config)

        # Should have skipped (file still exists, not a symlink)
        assert not conflict.is_symlink()
        assert conflict.read_text() == "existing content"

    def test_overwrite_removes_and_links(self, tmp_path: Path):
        config = _make_config(tmp_path)
        git_dir = config.dotfiles_root / "git"
        git_dir.mkdir()
        src = git_dir / ".gitconfig"
        src.write_text("[user]")

        conflict = config.home / ".gitconfig"
        conflict.write_text("old content")

        with patch("cli.symlinks._read_char", return_value="o"):
            setup_dotfiles(config)

        assert conflict.is_symlink()
        assert conflict.resolve() == src.resolve()

    def test_backup_renames_and_links(self, tmp_path: Path):
        config = _make_config(tmp_path)
        git_dir = config.dotfiles_root / "git"
        git_dir.mkdir()
        src = git_dir / ".gitconfig"
        src.write_text("[user]")

        conflict = config.home / ".gitconfig"
        conflict.write_text("old content")

        with patch("cli.symlinks._read_char", return_value="b"):
            setup_dotfiles(config)

        assert conflict.is_symlink()
        backup = config.home / ".gitconfig.backup"
        assert backup.exists()
        assert backup.read_text() == "old content"

    def test_skip_all_skips_remaining(self, tmp_path: Path):
        config = _make_config(tmp_path)
        for name in ["git", "vim"]:
            mod_dir = config.dotfiles_root / name
            mod_dir.mkdir()
            (mod_dir / f".{name}config").write_text("content")
            (config.home / f".{name}config").write_text("existing")

        with patch("cli.symlinks._read_char", return_value="S"):
            setup_dotfiles(config)

        # Both should be skipped (not symlinks)
        assert not (config.home / ".gitconfig").is_symlink()
        assert not (config.home / ".vimconfig").is_symlink()

    def test_overwrite_all_overwrites_remaining(self, tmp_path: Path):
        config = _make_config(tmp_path)
        for name in ["git", "vim"]:
            mod_dir = config.dotfiles_root / name
            mod_dir.mkdir()
            (mod_dir / f".{name}config").write_text("content")
            (config.home / f".{name}config").write_text("existing")

        with patch("cli.symlinks._read_char", return_value="O"):
            setup_dotfiles(config)

        assert (config.home / ".gitconfig").is_symlink()
        assert (config.home / ".vimconfig").is_symlink()
