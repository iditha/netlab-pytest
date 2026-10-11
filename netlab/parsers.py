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
