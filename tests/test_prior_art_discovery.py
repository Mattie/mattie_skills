"""Include the dependency-free Node discovery tests in the repository test command."""
from pathlib import Path
import shutil
import subprocess

import pytest


def test_public_catalog_discovery() -> None:
    """Run offline request/response scenarios with Node's built-in test runner."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js 20+ is required for service discovery tests")
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [node, "--test", "tests/prior-art-discovery.test.mjs"],
        cwd=root, capture_output=True, text=True, timeout=30, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
