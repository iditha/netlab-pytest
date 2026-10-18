import subprocess
import logging

logger = logging.getLogger(__name__)

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
        logger.info("%s $ %s", node, " ".join(command))
        result = subprocess.run(
            ["docker", "exec", f"clab-{self.name}-{node}", *command],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        logger.debug("%s exit=%s output:\n%s", node, result.returncode, result.stdout)
        return result    
