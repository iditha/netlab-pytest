import pytest

from netlab.lab import Lab


@pytest.fixture(scope="session")
def lab():
    lab = Lab("topologies/basic.clab.yml", name="basic")
    lab.deploy()
    yield lab
    lab.destroy()