import pytest

from netlab.parsers import parse_ospf_neighbors, route_next_hops

OSPF_NEIGHBORS = """{
  "neighbors": {
    "10.255.0.1": [
      {
        "nbrState": "Full/-",
        "ifaceName": "eth1:10.1.1.2",
        "ifaceAddress": "10.1.1.1"
      }
    ],
    "10.255.0.2": [
      {
        "nbrState": "Full/-",
        "ifaceName": "eth2:10.2.1.2",
        "ifaceAddress": "10.2.1.1"
      }
    ]
  }
}"""


def test_parse_ospf_neighbors():
    neighbors = parse_ospf_neighbors(OSPF_NEIGHBORS)
    by_id = {neighbor.router_id: neighbor for neighbor in neighbors}
    assert set(by_id) == {"10.255.0.1", "10.255.0.2"}
    assert by_id["10.255.0.1"].state == "Full"
    assert by_id["10.255.0.1"].interface == "eth1"
    assert by_id["10.255.0.1"].address == "10.1.1.1"


def test_parse_ospf_neighbors_empty():
    assert parse_ospf_neighbors('{"neighbors": {}}') == []


@pytest.mark.parametrize(
    "route, expected",
    [
        (
            {
                "dst": "192.168.2.0/24",
                "nexthops": [
                    {"gateway": "10.1.1.1"},
                    {"gateway": "10.2.1.1"},
                ],
            },
            {"10.1.1.1", "10.2.1.1"},
        ),
        ({"dst": "10.2.2.0/24", "gateway": "10.2.1.1"}, {"10.2.1.1"}),
        ({"dst": "10.1.1.0/24", "dev": "eth1"}, set()),
    ],
    ids=["ecmp", "single-path", "connected"],
)
def test_route_next_hops(route, expected):
    assert set(route_next_hops(route)) == expected
