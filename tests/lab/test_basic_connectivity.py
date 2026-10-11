import pytest


@pytest.mark.parametrize(
    "target",
    ["10.0.1.1", "10.0.12.2", "10.0.2.10"],
    ids=["gateway-r1", "far-router-r2", "host2"],
)
def test_host1_reaches(lab, target):
    result = lab.ping("host1", target)
    assert result.received == result.transmitted, result.output


def test_host2_reaches_host1(lab):
    # The return direction is routed separately, so test it separately
    result = lab.ping("host2", "10.0.1.10")
    assert result.received == result.transmitted, result.output


def test_path_to_host2_crosses_two_routers(lab):
    result = lab.ping("host1", "10.0.2.10", count=1)
    assert result.received == 1, f"No reply from host2, can't check TTL\n{result.output}"
    assert result.ttl == 62, f"Expected 2 router hops (TTL 64 - 2 = 62)\n{result.output}"


def test_nonexistent_host_is_unreachable(lab):
    # Negative test: nothing has this address, so no replies should come back
    result = lab.ping("host1", "10.0.1.99", count=2)
    assert result.received == 0, result.output