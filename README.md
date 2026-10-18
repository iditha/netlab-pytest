# netlab-pytest

![tests](https://github.com/iditha/netlab-pytest/actions/workflows/tests.yml/badge.svg)

A pytest framework that builds a virtual network with [containerlab](https://containerlab.dev),
runs automated tests against it, and tears it down — locally or in GitHub Actions CI.

## Topology

```
host1 ──── r1 ──── r2 ──── host2
   10.0.1.0/24  10.0.12.0/24  10.0.2.0/24
```
Two Linux routers with static routes connect three networks.

## What's tested

| Area | What's verified |
|---|---|
| Connectivity | host1 reaches each hop (r1, r2, host2), and host2 reaches host1 (each direction is routed separately) |
| Path | TTL shows replies crossed exactly 2 routers |
| Routing state | Each router has the static route it needs, checked directly from its routing table (JSON) |
| Negative | An address with no device stays unreachable |
| Parsers (unit) | Ping output parsing: success, partial/total loss, host unreachable, unrecognized output |

## Project structure

```
netlab/
  lab.py        deploy/destroy the lab, run commands in nodes
  devices.py    Device, Host and Router classes
  parsers.py    turn command output into structured results
tests/
  unit/         fast tests, no lab needed
  lab/          tests against the running lab
topologies/     network definitions for containerlab
```

## Run it

Requires Linux with Docker and containerlab — or open the repo in GitHub Codespaces,
where the dev container has everything preconfigured.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m pytest tests/unit -v    # fast, no lab needed
python -m pytest -v               # everything (deploys and destroys the lab)
```

## CI

Every push runs two GitHub Actions jobs: unit tests first, then the lab tests,
which run only if the unit tests pass.

## Design decisions

- **Device classes:** tests call `host1.ping(host2.ip)` instead of raw `docker exec` commands,
  so how devices are reached can change without touching the tests.
- **Structured data over screen text:** routing tables are read as JSON (`ip -j route`)
  instead of parsing text meant for humans.
- **Session-scoped lab:** the lab is deployed once for all tests, since deploying is slow.
- **Clear failure messages:** asserts include the raw command output and check preconditions first,
  so failures can be debugged without rerunning.

## Roadmap

- [x] Basic topology and automated connectivity tests
- [x] CI with GitHub Actions
- [x] Unit tests, device classes and routing table checks
- [ ] Spine-leaf topology with OSPF/BGP (FRR)
- [ ] Failover tests: link down → traffic reroutes
- [ ] Fault injection and automatic diagnostics on failure