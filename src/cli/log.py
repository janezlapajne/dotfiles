from rich.console import Console

_console = Console()


def info(msg: str) -> None:
    _console.print(f"  [blue]\\[..][/blue] {msg}")


def user(msg: str) -> None:
    _console.print(f"  [yellow]\\[??][/yellow] {msg}")


def success(msg: str) -> None:
    _console.print(f"  [green]\\[OK][/green] {msg}")


def fail(msg: str) -> None:
    _console.print(f"  [red]\\[FAIL][/red] {msg}")
    raise SystemExit(1)


def warn(msg: str) -> None:
    _console.print(f"  [yellow]\\[WARN][/yellow] {msg}")
