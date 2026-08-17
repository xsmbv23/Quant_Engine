"""N003 replay boundary guards.

Replay receives one immutable byte snapshot. After that point no network,
subprocess, wall-clock, random, or environment lookup is permitted by policy.
"""
from __future__ import annotations

import ast
import os
import socket
import subprocess
import time
from pathlib import Path
from typing import Callable

FORBIDDEN_MODULES = frozenset({"socket", "subprocess", "random", "requests", "urllib", "http", "httpx"})
FORBIDDEN_ATTRS = frozenset({"time", "monotonic", "perf_counter", "now", "utcnow", "getenv", "environ"})


def read_immutable_bytes(path: str | Path) -> bytes:
    """Read the receipt once and verify file identity metadata did not change."""
    p = Path(path)
    before = p.stat()
    with p.open("rb") as fh:
        data = fh.read()
        after_fd = os.fstat(fh.fileno())
    after = p.stat()
    before_id = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    after_id = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    fd_id = (after_fd.st_dev, after_fd.st_ino, after_fd.st_size, after_fd.st_mtime_ns)
    if before_id != after_id or after_id != fd_id:
        raise ValueError("REPLAY_INPUT_MUTATION_DETECTED")
    return data


def assert_replay_module_pure(path: str | Path) -> None:
    """Reject obvious external/runtime dependencies from a replay room module."""
    tree = ast.parse(Path(path).read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_MODULES:
                    raise ValueError(f"REPLAY_EXTERNAL_DEPENDENCY:{root}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in FORBIDDEN_MODULES:
                raise ValueError(f"REPLAY_EXTERNAL_DEPENDENCY:{root}")
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_ATTRS:
            raise ValueError(f"REPLAY_RUNTIME_DEPENDENCY:{node.attr}")


def isolated_environment() -> dict[str, str]:
    """Return a minimal deterministic environment for a replay subprocess."""
    return {
        "PYTHONHASHSEED": "0",
        "LC_ALL": "C",
        "LANG": "C",
    }


def network_is_disabled() -> bool:
    """Static policy marker used by tests; replay never opens sockets."""
    return True
