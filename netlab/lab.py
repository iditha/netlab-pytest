import re
import subprocess
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


class Lab:
    """Deploys a containerlab topology and runs commands inside its nodes."""

    def __init__(self, topology: str, name: str):
        self.topology = topology
        self.name = name

    def deploy(self):
        # --reconfigure: if a previous run left the lab behind, rebuild it from scratch
        subprocess.run(
            ["containerlab", "deploy", "-t", self.topology, "--reconfigure"],
            check=True,
        )

    def destroy(self):
        subprocess.run(
            ["containerlab", "destroy", "-t", self.topology, "--cleanup"],
            check=True,
        )

    def exec(self, node: str, command: list[str], timeout: int = 30):
        """Run a command inside a node, like `docker exec clab-<lab>-<node> ...`."""
        return subprocess.run(
            ["docker", "exec", f"clab-{self.name}-{node}", *command],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def ping(self, node: str, target: str, count: int = 3) -> PingResult:
        # -W 1: wait at most 1 second for each reply, so failures are fast
        result = self.exec(node, ["ping", "-c", str(count), "-W", "1", target])
        return parse_ping(result.stdout)