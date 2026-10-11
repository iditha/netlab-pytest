import json
import subprocess

from netlab.lab import Lab
from netlab.parsers import PingResult, parse_ping


class Device:
    """A node in the lab. Base class for Host and Router."""

    def __init__(self, lab: Lab, name: str, ip: str):
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
        return any(route["dst"] == destination for route in self.routes())


class Host(Device):
    pass


class Router(Device):
    def add_route(self, destination: str, via: str):
        self.run(["ip", "route", "add", destination, "via", via])

    def delete_route(self, destination: str):
        self.run(["ip", "route", "del", destination])