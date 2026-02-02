"""Agent Arcade - Play games while AI agents think."""

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import re


_POETRY_VERSION_RE = re.compile(r'^version\s*=\s*"([^"]+)"\s*$')


def _read_pyproject_version() -> str | None:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    if not pyproject.exists():
        return None

    in_poetry = False
    try:
        for line in pyproject.read_text().splitlines():
            stripped = line.strip()
            if stripped == "[tool.poetry]":
                in_poetry = True
                continue
            if in_poetry and stripped.startswith("[") and stripped.endswith("]"):
                break
            if not in_poetry:
                continue
            match = _POETRY_VERSION_RE.match(stripped)
            if match:
                return match.group(1)
    except OSError:
        return None
    return None


def _resolve_version() -> str:
    local_version = _read_pyproject_version()
    if local_version:
        return local_version
    try:
        return version("agent-arcade")
    except PackageNotFoundError:
        return "0+dev"


__version__ = _resolve_version()
