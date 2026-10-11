import pytest

from netlab.devices import Host, Router
from netlab.lab import Lab


@pytest.fixture(scope="session")
def lab():
    lab = Lab("topologies/basic.clab.yml", name="basic")
    lab.deploy()
    yield lab
    lab.destroy()


@pytest.fixture(scope="session")
def host1(lab):
    return Host(lab, "host1", ip="10.0.1.10")


@pytest.fixture(scope="session")
def host2(lab):
    return Host(lab, "host2", ip="10.0.2.10")


@pytest.fixture(scope="session")
def r1(lab):
    return Router(lab, "r1", ip="10.0.1.1")


@pytest.fixture(scope="session")
def r2(lab):
    return Router(lab, "r2", ip="10.0.12.2")