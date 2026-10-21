import pytest


def test_host1_reaches_host2(host1, host2):
    result = host1.ping(host2.ip)
    assert result.received == result.transmitted, result.output


def test_host2_reaches_host1(host2, host1):
    result = host2.ping(host1.ip)
    assert result.received == result.transmitted, result.output


def test_path_crosses_three_routers(host1, host2):
    result = host1.ping(host2.ip, count=1)
    assert result.received == 1, f"No reply from {host2}, can't check TTL\n{result.output}"
    assert result.ttl == 61, f"Expected leaf -> spine -> leaf (TTL 64 - 3 = 61)\n{result.output}"


@pytest.mark.parametrize("router_name", ["spine1", "spine2", "leaf1", "leaf2"])
def test_host1_reaches_router_loopbacks(host1, router_name, request):
    router = request.getfixturevalue(router_name)
    result = host1.ping(router.ip)
    assert result.received == result.transmitted, f"{router}\n{result.output}"
