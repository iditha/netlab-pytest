import pytest


@pytest.mark.parametrize(
    "router_name, destination",
    [
        ("r1", "10.0.2.0/24"),
        ("r2", "10.0.1.0/24"),
    ],
    ids=["r1-knows-host2-network", "r2-knows-host1-network"],
)
def test_router_has_static_route(router_name, destination, request):
    router = request.getfixturevalue(router_name)
    assert router.has_route(destination), f"{router} is missing a route to {destination}:\n{router.routes()}"