import pytest

from netlab.wait import wait_until


def test_returns_when_condition_becomes_true():
    calls = []

    def condition():
        calls.append(1)
        return len(calls) >= 3

    wait_until(condition, timeout=1, interval=0.01)
    assert len(calls) == 3


def test_times_out_with_clear_message():
    with pytest.raises(TimeoutError, match="waiting for the thing"):
        wait_until(lambda: False, timeout=0.05, interval=0.01, message="the thing")


def test_ignored_errors_count_as_not_ready():
    calls = []

    def condition():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError("daemon still starting")
        return True

    wait_until(condition, timeout=1, interval=0.01, ignore=(RuntimeError,))
    assert len(calls) == 3


def test_other_errors_are_not_hidden():
    with pytest.raises(ZeroDivisionError):
        wait_until(lambda: 1 / 0, timeout=1, interval=0.01)
