import pytest

from netlab.lab import parse_ping

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


def test_successful_ping():
    result = parse_ping(SUCCESS)
    assert result.transmitted == 3
    assert result.received == 3
    assert result.ttl == 62
    assert result.loss_percent == 0


def test_total_loss_has_no_ttl():
    result = parse_ping(TOTAL_LOSS)
    assert result.received == 0
    assert result.ttl is None
    assert result.loss_percent == 100


def test_partial_loss():
    result = parse_ping(PARTIAL_LOSS)
    assert result.received == 2
    assert result.loss_percent == pytest.approx(33.33, abs=0.01)


def test_host_unreachable_with_errors():
    result = parse_ping(HOST_UNREACHABLE)
    assert result.transmitted == 2
    assert result.received == 0


def test_output_is_kept_for_debugging():
    assert parse_ping(SUCCESS).output == SUCCESS


def test_unrecognized_output_raises():
    with pytest.raises(ValueError, match="Could not parse"):
        parse_ping("ping: unknown host")