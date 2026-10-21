# netlab-pytest

![tests](https://github.com/iditha/netlab-pytest/actions/workflows/tests.yml/badge.svg)

A pytest framework that builds a virtual network with [containerlab](https://containerlab.dev),
runs automated tests against it, and tears it down — locally or in GitHub Actions CI.

## Basic topology

```
host1 ──── r1 ──── r2 ──── host2
   10.0.1.0/24  10.0.12.0/24  10.0.2.0/24
```
Two Linux routers with static routes connect three networks.

## Spine-leaf topology

```
     spine1        spine2
       │  ╲        ╱  │
       │    ╲    ╱    │
       │      ╳       │
       │    ╱    ╲    │
       │  ╱        ╲  │
     leaf1          leaf2
       │              │
     host1          host2
```
Two FRR spines connect two FRR leaves, each serving a host. OSPF advertises
router loopbacks and host networks, with both spines providing ECMP paths
between the leaves.

## What's tested

| Area | What's verified |
|---|---|
| Connectivity | host1 reaches each hop (r1, r2, host2), and host2 reaches host1 (each direction is routed separately) |
| Path | TTL shows the hop count: 2 routers in the basic lab, 3 (leaf → spine → leaf) in spine-leaf |
| Routing state | Each router has the static route it needs, checked directly from its routing table (JSON) |
| Negative | An address with no device stays unreachable |
| Spine-leaf | OSPF adjacencies, OSPF-learned routes, ECMP next hops, host connectivity and router loopback reachability |
| Unit tests | Ping/OSPF parsing, route next-hop extraction and convergence-wait behavior |

## Project structure

```
netlab/
  lab.py           deploy/destroy the lab, run commands in nodes
  devices.py       Device, Host, Router and FrrRouter classes
  parsers.py       turn command output into structured results
  wait.py          poll until the network is ready (no fixed sleeps)
tests/
  unit/            fast tests, no lab needed (sample outputs in unit/data/)
  lab/basic/       tests for the two-router static-route lab
  lab/spine_leaf/  tests for the OSPF spine-leaf lab
topologies/        network definitions for containerlab
```

## Run it

Requires Linux with Docker and containerlab — or open the repo in GitHub Codespaces,
where the dev container has everything preconfigured.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m pytest tests/unit -v              # fast, no lab needed
python -m pytest tests/lab/spine_leaf -v    # one lab only
python -m pytest -v                         # everything (deploys and destroys the labs)
```

To watch the commands sent to each device, add `--log-cli-level=INFO`.

## CI

Every push runs two GitHub Actions jobs: linting (ruff) and unit tests first,
then the lab tests, which run only if the first job passes.

## Design decisions

- **Device classes:** tests call `host1.ping(host2.ip)` instead of raw `docker exec` commands,
  so how devices are reached can change without touching the tests. `FrrRouter` extends
  `Router` with routing-protocol state (OSPF neighbors via `vtysh`).
- **Structured data over screen text:** routing tables and OSPF state are read as JSON
  (`ip -j route`, `show ip ospf neighbor json`) instead of parsing text meant for humans.
- **Polling, not sleeping:** after deploy, tests wait until OSPF has actually converged
  (neighbors Full, ECMP routes installed) instead of a fixed `sleep`, which avoids flaky tests.
- **Session-scoped labs:** each lab is deployed once for all its tests, since deploying is slow,
  and is always destroyed afterwards — even if setup fails.
- **Clear failure messages:** asserts include the raw command output and check preconditions first,
  so failures can be debugged without rerunning.

## Roadmap

- [x] Basic topology and automated connectivity tests
- [x] CI with GitHub Actions
- [x] Unit tests, device classes and routing table checks
- [x] Spine-leaf topology with OSPF (FRR)
- [ ] Failover tests: link down → traffic reroutes
- [ ] BGP in the spine-leaf fabric
- [ ] Fault injection and automatic diagnostics on failure