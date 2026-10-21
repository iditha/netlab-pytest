import json
import subprocess

from netlab.lab import Lab
from netlab.parsers import (
    OspfNeighbor,
    PingResult,
    parse_ospf_neighbors,
    parse_ping,
    route_next_hops,
)


class Device:
    """A node in the lab. Base class for Host and Router."""

    def __init__(self, lab: Lab, name: str, ip: str | None = None):
        self.lab = lab
        self.name = name
        self.ip = ip  # main lab address, used as a ping target

    def __repr__(self):
        return f"{type(self).__name__}({self.name}, {self.ip})"

    def run(self, command: list[str]) -> subprocess.CompletedProcess:
        return self.lab.exec(self.name, command)

    def ping(self, target: str, count: int = 3) -> PingResult:
        # -W 1: wait at most 1 second for each reply, so failures are fast
        result = self.run(["ping", "-c", str(count), "-W", "1", target])
        return parse_ping(result.stdout)

    def routes(self) -> list[dict]:
        """The routing table as structured data, from `ip -j route` (JSON)."""
        result = self.run(["ip", "-j", "route"])
        return json.loads(result.stdout)

    def has_route(self, destination: str) -> bool:
        return self.route(destination) is not None

    def route(self, destination: str) -> dict | None:
        """Return the route for exactly this destination, if present."""
        return next((route for route in self.routes() if route["dst"] == destination), None)

    def next_hops(self, destination: str) -> list[str]:
        route = self.route(destination)
        return route_next_hops(route) if route is not None else []


class Host(Device):
    pass


class Router(Device):
    def add_route(self, destination: str, via: str):
        self.run(["ip", "route", "add", destination, "via", via])

    def delete_route(self, destination: str):
        self.run(["ip", "route", "del", destination])


class FrrRouter(Router):
    """A router running FRR, with access to OSPF state via vtysh."""

    def vtysh(self, command: str) -> str:
        result = self.run(["vtysh", "-c", command])
        if result.returncode != 0:
            raise RuntimeError(f"vtysh failed on {self.name}: {command}\n{result.stderr}")
        return result.stdout

    def ospf_neighbors(self) -> list[OspfNeighbor]:
        return parse_ospf_neighbors(self.vtysh("show ip ospf neighbor json"))

    def full_ospf_neighbors(self) -> set[str]:
        """Return router IDs for neighbors whose adjacency is fully established."""
        return {neighbor.router_id for neighbor in self.ospf_neighbors() if neighbor.state == "Full"}