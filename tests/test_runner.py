import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from cli.runner import command_exists, run


class TestRun:
    def test_run_list_command(self, mocker):
        mock_run = mocker.patch("cli.runner.subprocess.run")
        mock_run.return_value = subprocess.CompletedProcess(
            args=["echo", "hello"], returncode=0, stdout="hello\n", stderr=""
        )
        result = run(["echo", "hello"])
        mock_run.assert_called_once_with(
            ["echo", "hello"],
            shell=False,
            cwd=None,
            check=True,
            capture_output=False,
            text=True,
        )
        assert result.returncode == 0

    def test_run_string_command_with_shell(self, mocker):
        mock_run = mocker.patch("cli.runner.subprocess.run")
        mock_run.return_value = subprocess.CompletedProcess(
            args="echo hello", returncode=0
        )
        run("echo hello", shell=True)
        mock_run.assert_called_once_with(
            "echo hello",
            shell=True,
            cwd=None,
            check=True,
            capture_output=False,
            text=True,
        )

    def test_run_with_cwd(self, mocker, tmp_path: Path):
        mock_run = mocker.patch("cli.runner.subprocess.run")
        mock_run.return_value = subprocess.CompletedProcess(args=["ls"], returncode=0)
        run(["ls"], cwd=tmp_path)
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["cwd"] == tmp_path

    def test_run_with_capture(self, mocker):
        mock_run = mocker.patch("cli.runner.subprocess.run")
        mock_run.return_value = subprocess.CompletedProcess(
            args=["cmd"], returncode=0, stdout="output", stderr=""
        )
        result = run(["cmd"], capture=True)
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["capture_output"] is True

    def test_run_check_false_no_exception(self, mocker):
        mock_run = mocker.patch("cli.runner.subprocess.run")
        mock_run.return_value = subprocess.CompletedProcess(
            args=["fail"], returncode=1
        )
        result = run(["fail"], check=False)
        assert result.returncode == 1

    def test_run_check_true_raises_on_failure(self, mocker):
        mock_run = mocker.patch("cli.runner.subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(1, "bad")
        with pytest.raises(subprocess.CalledProcessError):
            run(["bad"], check=True)


class TestCommandExists:
    def test_existing_command(self, mocker):
        mocker.patch("cli.runner.shutil.which", return_value="/usr/bin/git")
        assert command_exists("git") is True

    def test_missing_command(self, mocker):
        mocker.patch("cli.runner.shutil.which", return_value=None)
        assert command_exists("nonexistent") is False
