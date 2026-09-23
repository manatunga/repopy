"""
Layer responsible for workspace metadata collection. Extracts needed data
and information regarding runtime version, project name, git branch, etc.
"""

from __future__ import annotations

import sys
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Self
from urllib.parse import urlparse
from importlib.metadata import distributions
import venv

from repopy.os_detector import is_windows

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

@dataclass(frozen=True)
class WorkspaceInfo:
    python_version: str
    executable_path: Path
    project_root: Path
    project_name: str | None = None
    project_version: str | None = None
    git_branch: str | None = None
    latest_commit_hash: str | None = None
    git_remote: str | None = None
    is_venv_active: bool = False
    package_count: int | None = None
    packages: list[str] | None = None

    def _get_git_info(project_root: Path):
        """Class method to extract git repository metadata"""
        def _run_git(args: list[str], cwd: Path) -> str | None:
            try:
                result = subprocess.run(
                    ["git", *args],
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    check=False
                )
                output = result.stdout.strip()    
                return output if result.returncode == 0 and output else None

            except FileNotFoundError:
                return None

    def _sanitize_remote_url(raw_url: str) -> str:
        """Helper function for _get_git_info to parse remote URLs"""
        if raw_url.startswith(("http://", "https://")):
            parsed = urlparse(raw_url)

            if "@" in parsed.netloc:
                host_info = parsed.hostname or ""
                if parsed.port:
                    host_info = f"{host_info}:{parsed.port}"

                return parsed._replace(netloc=host_info).geturl()    

        return raw_url

    def _get_project_meta(project_root: Path) -> tuple[str | None, str | None]:
        """Class method to safely inspects pyproject.toml"""
        try:
            toml_file = project_root / "pyproject.toml"

            if not toml_file.is_file():
                return (None, None)

            with open(toml_file, "rb") as f:
                config = tomllib.load(f)

            project_table = config.get("project", {})
            name = project_table.get("name")
            version = project_table.get("version")

            if not name or not version:
                poetry_table = config.get("tool", {}).get("poetry", {})
                name = name or poetry_table.get("name")
                version = version or poetry_table.get("version")

            return (name, version)

        except (tomllib.TOMLDecodeError, OSError):
            return (None, None)

    def _find_site_packages(venv_path: Path) -> Path | None:
        """Helper function for _get_venv_info to locate site packages"""
        if is_windows():
            win_sp = venv_path / "Lib" / "site-packages"
            return win_sp if win_sp.is_dir() else None

        lib_dir = venv_path / "lib"
        if lib_dir.is_dir():
            for py_dir in lib_dir.glob("python3.*"):
                sp = py_dir / "site-packages"
                if sp.is_dir():
                    return sp

        return None

    def _get_venv_info(project_root: Path) -> tuple[
        bool, int | None, list[str] | None
    ]:
        """Class method that extracts runtime, venv and dependency data"""
        VENV_CANDIDATES = (".venv", "venv", ".env", "env",)
        try:
            is_venv_active = sys.prefix != sys.base_prefix
            venv_path: Path | None = None
            
            if is_venv_active:
                venv_path = Path(sys.prefix)
            else:    
                for candidate in VENV_CANDIDATES:
                    candidate_path = project_root / candidate

                    if (
                        candidate_path.is_dir()
                        and (candidate_path / "pyvenv.cfg").is_file()
                    ):
                        venv_path = candidate_path
                        break

            if not venv_path:
                return (False, None, None)

            sp_dir = WorkspaceInfo._find_site_packages(venv_path)
            if not sp_dir:
                return (is_venv_active, None, None)

            deps = []
            dists = distributions(path=[str(sp_dir)])
            for dist in dists:
                name = dist.metadata["Name"]

                if name:
                    deps.append(f"{name}=={dist.version}")

            deps.sort()
            return (is_venv_active, len(deps), deps)

        except OSError:
            return (False, None, None)

    @classmethod
    def from_project_root(cls, project_root: Path) -> "WorkspaceInfo":
        """Factory method to aggregate project, git, runtime and venv metadata"""
        branch, commit, raw_url = cls._get_git_info(project_root)
        remote = cls._sanitize_remote_url(raw_url)
        name, version = cls._get_project_meta(project_root)
        is_active, pkg_count, pkg_list = cls._get_venv_info(project_root)

        python_version = sys.version.split()[0]
        python_path = Path(sys.executable)

        return cls(
            python_version=python_version,
            executable_path=python_path,
            project_root=project_root,
            project_name=name,
            project_version=version,
            git_branch=branch,
            latest_commit_hash=commit,
            git_remote=remote,
            is_venv_active=is_active,
            package_count=pkg_count,
            packages=pkg_list,
        )
         