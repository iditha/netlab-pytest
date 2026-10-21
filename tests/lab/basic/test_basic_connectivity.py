import pytest


@pytest.mark.parametrize("target", ["r1", "r2", "host2"])
def test_host1_reaches(host1, target, request):
    target_device = request.getfixturevalue(target)
    result = host1.ping(target_device.ip)
    assert result.received == result.transmitted, result.output


def test_host2_reaches_host1(host2, host1):
    # The return direction is routed separately, so test it separately
    result = host2.ping(host1.ip)
    assert result.received == result.transmitted, result.output


def test_path_to_host2_crosses_two_routers(host1, host2):
    result = host1.ping(host2.ip, count=1)
    assert result.received == 1, f"No reply from {host2}, can't check TTL\n{result.output}"
    assert result.ttl == 62, f"Expected 2 router hops (TTL 64 - 2 = 62)\n{result.output}"


def test_nonexistent_host_is_unreachable(host1):
    # Negative test: nothing has this address, so no replies should come back
    result = host1.ping("10.0.1.99", count=2)
    assert result.received == 0, result.output