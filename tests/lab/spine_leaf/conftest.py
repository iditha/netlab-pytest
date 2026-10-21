import pytest

from netlab.devices import FrrRouter, Host
from netlab.lab import Lab
from netlab.wait import wait_until

ROUTERS = {
    "spine1": "10.255.0.1",
    "spine2": "10.255.0.2",
    "leaf1": "10.255.0.11",
    "leaf2": "10.255.0.12",
}


def fabric_converged(lab: Lab) -> bool:
    """Check OSPF adjacencies and ECMP routes are established."""
    routers = {name: FrrRouter(lab, name) for name in ROUTERS}
    if any(len(router.full_ospf_neighbors()) < 2 for router in routers.values()):
        return False
    return (
        len(routers["leaf1"].next_hops("192.168.2.0/24")) == 2
        and len(routers["leaf2"].next_hops("192.168.1.0/24")) == 2
    )


@pytest.fixture(scope="session")
def lab():
    lab = Lab("topologies/spine-leaf/spine-leaf.clab.yml", name="spine-leaf")
    lab.deploy()
    try:
        wait_until(
            lambda: fabric_converged(lab),
            timeout=90,
            interval=2,
            message="OSPF to converge",
            ignore=(RuntimeError, ValueError),
        )
        yield lab
    finally:
        lab.destroy()


@pytest.fixture(scope="session")
def spine1(lab):
    return FrrRouter(lab, "spine1", ip=ROUTERS["spine1"])


@pytest.fixture(scope="session")
def spine2(lab):
    return FrrRouter(lab, "spine2", ip=ROUTERS["spine2"])


@pytest.fixture(scope="session")
def leaf1(lab):
    return FrrRouter(lab, "leaf1", ip=ROUTERS["leaf1"])


@pytest.fixture(scope="session")
def leaf2(lab):
    return FrrRouter(lab, "leaf2", ip=ROUTERS["leaf2"])


@pytest.fixture(scope="session")
def host1(lab):
    return Host(lab, "host1", ip="192.168.1.10")


@pytest.fixture(scope="session")
def host2(lab):
    return Host(lab, "host2", ip="192.168.2.10")
