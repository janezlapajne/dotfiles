# Repo

Personal macOS dotfiles. The `dot` CLI (Typer + Rich, Python ≥ 3.12, installed via `uv tool install --editable .`) bootstraps Homebrew packages, runs per-tool modules, and resolves symlinks into `$HOME`. `Config.load()` hardcodes the working tree to `~/.dotfiles` — do not relocate it.

# Commands

```bash
dot                    # update: git pull --ff-only → packages → module install() (no setup, no symlinks)
dot --setup            # full bootstrap: packages → all install() → all setup() → symlinks
dot --symlink-only     # re-resolve conf/symlinks.toml only
dot --env-update       # regenerate .env.example from .env (strips values, keeps keys + comments)
dot -e / --edit        # open the dotfiles dir in $EDITOR (falls back to DEFAULT_EDITOR)

uv run ruff check .    # lint (py312, line-length 100, double quotes)
uv run ruff format .
uv run pytest          # no tests/ dir yet — create it before adding tests
```

# Layout

- `src/cli/` — CLI internals. Use the helpers, not raw stdlib:
  - `cli.runner.run(cmd, *, shell=False, cwd=None, check=True, capture=False)` — logs and runs; defaults to `check=True`.
  - `cli.runner.command_exists(name)` — `shutil.which` wrapper.
  - `cli.log.{info,user,success,warn,fail}` — Rich-formatted output. **`log.fail()` raises `SystemExit(1)`** — it is not a no-op logger.
- `src/modules/` — one file per tool, subclassing `DotfileModule`. Registered in `modules/__init__.py::_MODULE_CLASSES`. **`ZshModule` must remain first** (oh-my-zsh is a dependency for the rest); other modules are alphabetical.
- `conf/packages.toml` — `[brew].packages`, `[brew].casks`, optional `[npm].packages`.
- `conf/symlinks.toml` — `[symlinks].root = [...]` links to `$HOME/<basename>`; `[symlinks.targets]."rel/path" = "dir"` links to `$HOME/<dir>/<basename>`.
- `conf/dotfiles/<tool>/` — actual files referenced by `symlinks.toml`.
- `conf/bin/` and `conf/functions/` — added to `$PATH` by zsh init.

# Module contract

```python
class FooModule(DotfileModule):
    def install(self) -> None: ...   # idempotent; runs on `dot` AND `dot --setup`
    def setup(self) -> None: ...     # one-time / interactive; runs only on `dot --setup`
```

- Read user values via `self.env("KEY")` (returns `""` if unset). Never touch `os.environ` directly.
- Bootstrap runs **two passes**: all `install()` first, then all `setup()`. Don't rely on a sibling module's `setup()` having run from inside an `install()`.
- Exceptions inside `install`/`setup` are caught by `run_install`/`run_setup` — but the catch-handler calls `log.fail()`, which raises `SystemExit(1)` and **aborts the bootstrap**. Only let an exception escape if you genuinely want to stop everything; otherwise catch and `log.warn()` inside the module.
- For one-time work, gate on the artifact (e.g. `if key_path.exists(): log.warn(...); return`) — `dot --setup` is rerun-safe.

# Symlink conflict prompts

On conflict the runner prompts skip / overwrite / backup / adopt; uppercase = sticky for the rest of the run; non-TTY stdin skips. **Adopt** moves the existing file *into* the repo and replaces it with a symlink (useful for migrating a config). Duplicate destinations across `symlinks.toml` are a hard error.

# Adding things

- New env var → add to `.env.example` (with empty value), read via `self.env("KEY")`. Run `dot --env-update` after editing `.env` to regenerate the example.
- New tool integration → `src/modules/<tool>.py` + register in `_MODULE_CLASSES` (alphabetical position).
- New dotfile → drop under `conf/dotfiles/<tool>/`, add an entry to `conf/symlinks.toml`. The runner skips entries whose `src` and `dst` both don't exist, so partial entries are safe to commit.
- New package → append to `conf/packages.toml`.

# Zsh loading conventions

Anything matching `conf/dotfiles/**/*.zsh` is sourced by `.zshrc`. By convention: `path.zsh` files load **first** (use for `$PATH`), `completion.zsh` files load **last** (use for completions).
