import pytest

from netlab.lab import parse_ping

# Real ping outputs captured from the lab, used as test input

SUCCESS = """PING 10.0.2.10 (10.0.2.10) 56(84) bytes of data.
64 bytes from 10.0.2.10: icmp_seq=1 ttl=62 time=0.102 ms
64 bytes from 10.0.2.10: icmp_seq=2 ttl=62 time=0.056 ms
64 bytes from 10.0.2.10: icmp_seq=3 ttl=62 time=0.057 ms

--- 10.0.2.10 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2086ms
"""

TOTAL_LOSS = """PING 10.0.2.10 (10.0.2.10) 56(84) bytes of data.

--- 10.0.2.10 ping statistics ---
3 packets transmitted, 0 received, 100% packet loss, time 2054ms
"""

PARTIAL_LOSS = """PING 10.0.2.10 (10.0.2.10) 56(84) bytes of data.
64 bytes from 10.0.2.10: icmp_seq=1 ttl=62 time=0.102 ms
64 bytes from 10.0.2.10: icmp_seq=3 ttl=62 time=0.057 ms

--- 10.0.2.10 ping statistics ---
3 packets transmitted, 2 received, 33.3333% packet loss, time 2086ms
"""

HOST_UNREACHABLE = """PING 10.0.1.99 (10.0.1.99) 56(84) bytes of data.
From 10.0.1.10 icmp_seq=1 Destination Host Unreachable
From 10.0.1.10 icmp_seq=2 Destination Host Unreachable

--- 10.0.1.99 ping statistics ---
2 packets transmitted, 0 received, +2 errors, 100% packet loss, time 1010ms
"""


@pytest.mark.parametrize(
    "sample, transmitted, received, ttl",
    [
        (SUCCESS, 3, 3, 62),
        (TOTAL_LOSS, 3, 0, None),
        (PARTIAL_LOSS, 3, 2, 62),
        (HOST_UNREACHABLE, 2, 0, None),
    ],
    ids=["success", "total-loss", "partial-loss", "host-unreachable"],
)
def test_parse_ping_counts_and_ttl(sample, transmitted, received, ttl):
    result = parse_ping(sample)
    assert result.transmitted == transmitted
    assert result.received == received
    assert result.ttl == ttl


@pytest.mark.parametrize(
    "sample, expected_loss",
    [
        (SUCCESS, 0),
        (TOTAL_LOSS, 100),
        (PARTIAL_LOSS, 33.33),
    ],
    ids=["success", "total-loss", "partial-loss"],
)
def test_loss_percent(sample, expected_loss):
    result = parse_ping(sample)
    assert result.loss_percent == pytest.approx(expected_loss, abs=0.01)


def test_output_is_kept_for_debugging():
    assert parse_ping(SUCCESS).output == SUCCESS


def test_unrecognized_output_raises():
    with pytest.raises(ValueError, match="Could not parse"):
        parse_ping("ping: unknown host")