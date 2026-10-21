import pytest

EXPECTED_NEIGHBORS = {
    "spine1": {"10.255.0.11", "10.255.0.12"},
    "spine2": {"10.255.0.11", "10.255.0.12"},
    "leaf1": {"10.255.0.1", "10.255.0.2"},
    "leaf2": {"10.255.0.1", "10.255.0.2"},
}


@pytest.mark.parametrize("router_name", EXPECTED_NEIGHBORS)
def test_ospf_neighbors_are_full(router_name, request):
    router = request.getfixturevalue(router_name)
    expected = EXPECTED_NEIGHBORS[router_name]
    assert router.full_ospf_neighbors() == expected, f"{router} neighbors: {router.ospf_neighbors()}"


@pytest.mark.parametrize(
    "leaf_name, remote_network",
    [("leaf1", "192.168.2.0/24"), ("leaf2", "192.168.1.0/24")],
)
def test_leaf_learns_remote_host_network_via_ospf(leaf_name, remote_network, request):
    leaf = request.getfixturevalue(leaf_name)
    route = leaf.route(remote_network)
    assert route is not None, f"{leaf} has no route to {remote_network}"
    assert route.get("protocol") == "ospf", f"{leaf} route was not learned via OSPF: {route}"


@pytest.mark.parametrize(
    "leaf_name, remote_network, expected_next_hops",
    [
        ("leaf1", "192.168.2.0/24", {"10.1.1.1", "10.2.1.1"}),
        ("leaf2", "192.168.1.0/24", {"10.1.2.1", "10.2.2.1"}),
    ],
)
def test_ecmp_uses_both_spines(leaf_name, remote_network, expected_next_hops, request):
    leaf = request.getfixturevalue(leaf_name)
    next_hops = set(leaf.next_hops(remote_network))
    assert next_hops == expected_next_hops, f"{leaf} route: {leaf.route(remote_network)}"
