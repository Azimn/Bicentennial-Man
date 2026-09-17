from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any


@dataclass(frozen=True, slots=True)
class DockerSandboxSpec:
    image: str = "python:3.11-slim"
    memory: str = "512m"
    cpus: str = "1.0"
    pids_limit: int = 64


class DockerCandidateSandbox:
    """Run generated surface-control code with only explicit candidate and state mounts.

    The container has no network, a read-only root filesystem, a read-only candidate mount, and one
    writable assigned state mount. DUCK, the Bicentennial repository, evaluators, sealed suites, and
    other candidates are not mounted.
    """

    def __init__(
        self,
        *,
        candidate_path: str | Path,
        state_root: str | Path,
        timeout: float = 120.0,
        spec: DockerSandboxSpec | None = None,
        docker_executable: str = "docker",
    ) -> None:
        self.candidate_path = Path(candidate_path).resolve()
        self.state_root = Path(state_root).resolve()
        self.timeout = float(timeout)
        self.spec = spec or DockerSandboxSpec()
        self.docker_executable = docker_executable

    def command(self) -> list[str]:
        if shutil.which(self.docker_executable) is None:
            raise RuntimeError(
                "Docker is required for generated candidate execution. "
                "Unsafe local execution is intentionally not the default."
            )
        self.state_root.mkdir(parents=True, exist_ok=True)
        return [
            self.docker_executable,
            "run",
            "--rm",
            "-i",
            "--network",
            "none",
            "--read-only",
            "--pids-limit",
            str(self.spec.pids_limit),
            "--memory",
            self.spec.memory,
            "--cpus",
            self.spec.cpus,
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "--mount",
            f"type=bind,source={self.candidate_path},target=/candidate/program.py,readonly",
            "--mount",
            f"type=bind,source={self.state_root},target=/state",
            self.spec.image,
            "python",
            "/candidate/program.py",
        ]

    def run_json(self, payload: dict[str, Any]) -> dict[str, Any]:
        request_payload = dict(payload)
        request_payload["state_root"] = "/state"
        completed = subprocess.run(
            self.command(),
            input=json.dumps(request_payload),
            text=True,
            capture_output=True,
            timeout=self.timeout,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"sandboxed candidate failed with exit code {completed.returncode}: "
                f"{completed.stderr.strip()}"
            )
        try:
            row = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"sandboxed candidate returned invalid JSON: {completed.stdout[:500]!r}") from exc
        if not isinstance(row, dict):
            raise RuntimeError("sandboxed candidate must return a JSON object")
        return row
