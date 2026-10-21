import json
import re
from dataclasses import dataclass


@dataclass
class PingResult:
    transmitted: int
    received: int
    ttl: int | None  # TTL of the last reply, None if no reply came back
    output: str      # full ping output, useful when a test fails

    @property
    def loss_percent(self) -> float:
        return 100 * (self.transmitted - self.received) / self.transmitted


def parse_ping(output: str) -> PingResult:
    stats = re.search(r"(\d+) packets transmitted, (\d+) received", output)
    if stats is None:
        raise ValueError(f"Could not parse ping output:\n{output}")
    ttls = re.findall(r"ttl=(\d+)", output)
    return PingResult(
        transmitted=int(stats.group(1)),
        received=int(stats.group(2)),
        ttl=int(ttls[-1]) if ttls else None,
        output=output,
    )


@dataclass
class OspfNeighbor:
    router_id: str
    state: str
    interface: str
    address: str


def parse_ospf_neighbors(output: str) -> list[OspfNeighbor]:
    """Parse FRR's ``show ip ospf neighbor json`` output."""
    data = json.loads(output)
    neighbors = []
    for router_id, entries in data.get("neighbors", {}).items():
        for entry in entries:
            neighbors.append(
                OspfNeighbor(
                    router_id=router_id,
                    state=entry["nbrState"].split("/")[0],
                    interface=entry["ifaceName"].split(":")[0],
                    address=entry["ifaceAddress"],
                )
            )
    return neighbors


def route_next_hops(route: dict) -> list[str]:
    """Return gateway addresses for single-path or ECMP routes."""
    if "nexthops" in route:
        return [hop["gateway"] for hop in route["nexthops"] if "gateway" in hop]
    if "gateway" in route:
        return [route["gateway"]]
    return []
