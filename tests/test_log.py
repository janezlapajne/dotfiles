import pytest

from cli import log


class TestLog:
    def test_info_does_not_raise(self, capsys):
        log.info("test message")

    def test_user_does_not_raise(self, capsys):
        log.user("test prompt")

    def test_success_does_not_raise(self, capsys):
        log.success("test success")

    def test_warn_does_not_raise(self, capsys):
        log.warn("test warning")

    def test_fail_raises_system_exit(self):
        with pytest.raises(SystemExit) as exc_info:
            log.fail("test failure")
        assert exc_info.value.code == 1
