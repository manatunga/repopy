"""
Automated test suite for workspace metadata fetcher.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
import types
from pathlib import Path

import pytest

from repopy.info import WorkspaceInfo


def test_find_site_packages_unix(monkeypatch, tmp_path):
    sp_dir = tmp_path / "lib" / "python3.12" / "site-packages"
    sp_dir.mkdir(parents=True)

    monkeypatch.setattr("repopy.info.is_windows", lambda: False)
    sp = WorkspaceInfo._find_site_packages(tmp_path)

    assert sp == sp_dir


def test_find_site_packages_windows(monkeypatch, tmp_path):
    sp_dir = tmp_path / "Lib" / "site-packages"
    sp_dir.mkdir(parents=True)

    monkeypatch.setattr("repopy.info.is_windows", lambda: True)
    sp = WorkspaceInfo._find_site_packages(tmp_path)

    assert sp == sp_dir


def test_find_site_packages_unix_no_sp(monkeypatch, tmp_path):
    monkeypatch.setattr("repopy.info.is_windows", lambda: False)
    sp = WorkspaceInfo._find_site_packages(tmp_path)
    assert sp is None


def test_find_site_packages_windows_no_sp(monkeypatch, tmp_path):
    monkeypatch.setattr("repopy.info.is_windows", lambda: True)
    sp = WorkspaceInfo._find_site_packages(tmp_path)
    assert sp is None


def test_get_venv_info_active_venv(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "prefix", "/fake/venv")
    monkeypatch.setattr(sys, "base_prefix", "/fake/base")
    monkeypatch.setattr(WorkspaceInfo, "_find_site_packages", lambda path: tmp_path)

    class DummyDist:
        def __init__(self, name: str, version: str):
            self.metadata = {"Name": name}
            self.version = version

    monkeypatch.setattr(
        "repopy.info.distributions",
        lambda path=None: [
            DummyDist("fastapi", "0.3.1"),
            DummyDist("click", "0.5.4"),
        ],
    )

    venv_data = WorkspaceInfo._get_venv_info(tmp_path)

    assert venv_data[0] is True
    assert venv_data[1] == 2
    assert venv_data[2] == ["click==0.5.4", "fastapi==0.3.1"]


def test_get_venv_info_inactive_venv(monkeypatch, tmp_path):
    venv_path = tmp_path / ".venv"
    venv_path.mkdir()
    (venv_path / "pyvenv.cfg").touch()

    monkeypatch.setattr(sys, "prefix", "/fake/base")
    monkeypatch.setattr(sys, "base_prefix", "/fake/base")
    monkeypatch.setattr(WorkspaceInfo, "_find_site_packages", lambda path: venv_path)

    class DummyDist:
        def __init__(self, name: str, version: str):
            self.metadata = {"Name": name}
            self.version = version

    monkeypatch.setattr(
        "repopy.info.distributions",
        lambda path=None: [DummyDist("fastapi", "0.3.1"), DummyDist("click", "0.5.4")],
    )

    venv_data = WorkspaceInfo._get_venv_info(tmp_path)

    assert venv_data[0] is False
    assert venv_data[1] == 2
    assert venv_data[2] == ["click==0.5.4", "fastapi==0.3.1"]


def test_get_venv_info_no_venv(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "prefix", "/fake/base")
    monkeypatch.setattr(sys, "base_prefix", "/fake/base")

    venv_data = WorkspaceInfo._get_venv_info(tmp_path)

    assert venv_data == (False, None, None)


def test_get_venv_info_no_sp(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "prefix", "/fake/venv")
    monkeypatch.setattr(sys, "base_prefix", "/fake/base")
    monkeypatch.setattr(WorkspaceInfo, "_find_site_packages", lambda path: None)

    venv_data = WorkspaceInfo._get_venv_info(tmp_path)

    assert venv_data == (True, None, None)


def test_get_venv_info_handle_os_error(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "prefix", "/fake/venv")
    monkeypatch.setattr(sys, "base_prefix", "/fake/base")
    monkeypatch.setattr(WorkspaceInfo, "_find_site_packages", lambda path: tmp_path)

    def mock_error(path):
        raise OSError("Permission denied")

    monkeypatch.setattr(WorkspaceInfo, "_find_site_packages", mock_error)

    venv_data = WorkspaceInfo._get_venv_info(tmp_path)

    assert venv_data == (False, None, None)


@pytest.mark.parametrize(
    "raw_url, expected",
    [
        (
            "https://username:token@github.com/user/repo.git",
            "https://github.com/user/repo.git",
        ),
        (
            "https://username:token@github.com:8443/user/repo.git",
            "https://github.com:8443/user/repo.git",
        ),
        (
            "https://github.com/user/repo.git",
            "https://github.com/user/repo.git",
        ),
        (
            "git@github.com:user/repo.git",
            "git@github.com:user/repo.git",
        ),
        ("", ""),
    ],
)
def test_sanitize_remote_url(raw_url, expected):
    assert WorkspaceInfo._sanitize_remote_url(raw_url) == expected


def test_get_git_info_success(monkeypatch, tmp_path):
    def mock_subprocess_run(cmd, *args, **kwargs):
        cmd_str = " ".join(cmd)

        if "branch" in cmd_str:
            stdout = "main"
        elif "rev-parse" in cmd_str:
            stdout = "a1b2c3d"
        elif "remote" in cmd_str:
            stdout = "https://github.com/user/repo.git"
        else:
            stdout = ""

        class DummyProcess:
            returncode = 0

            def __init__(self, out: str):
                self.stdout = out

        return DummyProcess(stdout)

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    git_info = WorkspaceInfo._get_git_info(tmp_path)

    assert git_info == (
        "main",
        "a1b2c3d",
        "https://github.com/user/repo.git",
    )


def test_get_git_info_no_git(monkeypatch, tmp_path):
    def mock_error(*args, **kwargs):
        raise FileNotFoundError("git executable not found")

    monkeypatch.setattr(subprocess, "run", mock_error)
    git_info = WorkspaceInfo._get_git_info(tmp_path)

    assert git_info == (None, None, None)


def test_get_git_info_on_non_git_repo(monkeypatch, tmp_path):
    def mock_subprocess_run(*args, **kwargs):
        class ErrorProcess:
            def __init__(self):
                self.returncode = 128
                self.stdout = ""

        return ErrorProcess()

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    git_info = WorkspaceInfo._get_git_info(tmp_path)

    assert git_info == (None, None, None)


def test_get_git_info_empty_output(monkeypatch, tmp_path):
    def mock_subprocess_run(*args, **kwargs):
        class EmptySuccessProcess:
            def __init__(self):
                self.returncode = 0
                self.stdout = "    \n"

        return EmptySuccessProcess()

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    git_info = WorkspaceInfo._get_git_info(tmp_path)

    assert git_info == (None, None, None)


def test_get_git_info_partial_output(monkeypatch, tmp_path):
    def mock_subprocess_run(cmd, *args, **kwargs):
        cmd_str = " ".join(cmd)

        if "branch" in cmd_str:
            stdout = ""
            code = 1
        elif "rev-parse" in cmd_str:
            stdout = "a1b2c3d"
            code = 0
        elif "remote" in cmd_str:
            stdout = ""
            code = 1
        else:
            stdout = ""
            code = 1

        class DummyProcess:
            def __init__(self, out: str, code: int):
                self.stdout = out
                self.returncode = code

        return DummyProcess(stdout, code)

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    git_info = WorkspaceInfo._get_git_info(tmp_path)

    assert git_info == (None, "a1b2c3d", None)


def test_get_project_meta_standard_toml_success(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "my_project"
version = "0.1.0"
"""
    )

    project_info = WorkspaceInfo._get_project_meta(tmp_path)

    assert project_info == ("my_project", "0.1.0")


def test_get_project_meta_poetry_toml_success(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.poetry]
name = "my_project"
version = "0.1.0"
"""
    )

    project_info = WorkspaceInfo._get_project_meta(tmp_path)

    assert project_info == ("my_project", "0.1.0")


def test_get_project_meta_missing_toml(tmp_path):
    project_info = WorkspaceInfo._get_project_meta(tmp_path)
    assert project_info == (None, None)


def test_get_project_meta_invalid_toml_syntax(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = 0.1.0
"""
    )

    project_info = WorkspaceInfo._get_project_meta(tmp_path)

    assert project_info == (None, None)


def test_get_project_meta_missing_keys(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
"""
    )

    project_info = WorkspaceInfo._get_project_meta(tmp_path)

    assert project_info == (None, None)


def test_get_project_meta_handle_os_error(monkeypatch, tmp_path):
    def mock_error(*args, **kwargs):
        raise OSError("Permission deinied")

    monkeypatch.setattr(Path, "open", mock_error)
    project_info = WorkspaceInfo._get_project_meta(tmp_path)

    assert project_info == (None, None)


def test_from_project_root_success(monkeypatch, tmp_path):
    monkeypatch.setattr(
        WorkspaceInfo,
        "_get_git_info",
        lambda path: (
            "main",
            "a1b2c3d",
            "https://github.com/user/repo.git",
        ),
    )
    monkeypatch.setattr(
        WorkspaceInfo,
        "_get_project_meta",
        lambda path: (
            "my_project",
            "0.1.0",
        ),
    )
    monkeypatch.setattr(
        WorkspaceInfo,
        "_get_venv_info",
        lambda path: (True, 2, ["click==0.5.1", "fastapi==0.3.4"]),
    )
    monkeypatch.setattr(sys, "version", "3.12.0 (default, Jan 1 2026, 00:00:00) [GCC]")
    exec_path = tmp_path / ".venv" / "bin" / "python"
    monkeypatch.setattr(sys, "executable", str(exec_path))

    info = WorkspaceInfo.from_project_root(tmp_path)

    assert info.python_version == "3.12.0"
    assert info.executable_path == exec_path
    assert info.project_root == tmp_path
    assert info.project_name == "my_project"
    assert info.project_version == "0.1.0"
    assert info.git_branch == "main"
    assert info.latest_commit_hash == "a1b2c3d"
    assert info.git_remote == "https://github.com/user/repo.git"
    assert info.is_venv_active is True
    assert info.package_count == 2
    assert info.packages == ["click==0.5.1", "fastapi==0.3.4"]


def test_from_project_root_missing_git_info(monkeypatch, tmp_path):
    monkeypatch.setattr(
        WorkspaceInfo,
        "_get_git_info",
        lambda path: (None, None, None),
    )
    monkeypatch.setattr(
        WorkspaceInfo,
        "_get_project_meta",
        lambda path: (
            "my_project",
            "0.1.0",
        ),
    )
    monkeypatch.setattr(
        WorkspaceInfo,
        "_get_venv_info",
        lambda path: (True, 2, ["click==0.5.1", "fastapi==0.3.4"]),
    )
    monkeypatch.setattr(sys, "version", "3.12.0 (default, Jan 1 2026, 00:00:00) [GCC]")
    exec_path = tmp_path / ".venv" / "bin" / "python"
    monkeypatch.setattr(sys, "executable", str(exec_path))

    info = WorkspaceInfo.from_project_root(tmp_path)

    assert info.python_version == "3.12.0"
    assert info.executable_path == exec_path
    assert info.project_root == tmp_path
    assert info.project_name == "my_project"
    assert info.project_version == "0.1.0"
    assert info.git_branch == None
    assert info.latest_commit_hash == None
    assert info.git_remote == None
    assert info.is_venv_active is True
    assert info.package_count == 2
    assert info.packages == ["click==0.5.1", "fastapi==0.3.4"]


def test_from_project_root_missing_project_meta(monkeypatch, tmp_path):
    monkeypatch.setattr(
        WorkspaceInfo,
        "_get_git_info",
        lambda path: (
            "main",
            "a1b2c3d",
            "https://github.com/user/repo.git",
        ),
    )
    monkeypatch.setattr(
        WorkspaceInfo,
        "_get_project_meta",
        lambda path: (None, None),
    )
    monkeypatch.setattr(
        WorkspaceInfo,
        "_get_venv_info",
        lambda path: (True, 2, ["click==0.5.1", "fastapi==0.3.4"]),
    )
    monkeypatch.setattr(sys, "version", "3.12.0 (default, Jan 1 2026, 00:00:00) [GCC]")
    exec_path = tmp_path / ".venv" / "bin" / "python"
    monkeypatch.setattr(sys, "executable", str(exec_path))

    info = WorkspaceInfo.from_project_root(tmp_path)

    assert info.python_version == "3.12.0"
    assert info.executable_path == exec_path
    assert info.project_root == tmp_path
    assert info.project_name == None
    assert info.project_version == None
    assert info.git_branch == "main"
    assert info.latest_commit_hash == "a1b2c3d"
    assert info.git_remote == "https://github.com/user/repo.git"
    assert info.is_venv_active is True
    assert info.package_count == 2
    assert info.packages == ["click==0.5.1", "fastapi==0.3.4"]


def test_from_project_root_missing_venv_info(monkeypatch, tmp_path):
    monkeypatch.setattr(
        WorkspaceInfo,
        "_get_git_info",
        lambda path: (
            "main",
            "a1b2c3d",
            "https://github.com/user/repo.git",
        ),
    )
    monkeypatch.setattr(
        WorkspaceInfo,
        "_get_project_meta",
        lambda path: (
            "my_project",
            "0.1.0",
        ),
    )
    monkeypatch.setattr(
        WorkspaceInfo,
        "_get_venv_info",
        lambda path: (False, 0, []),
    )
    monkeypatch.setattr(sys, "version", "3.12.0 (default, Jan 1 2026, 00:00:00) [GCC]")
    exec_path = tmp_path / ".venv" / "bin" / "python"
    monkeypatch.setattr(sys, "executable", str(exec_path))

    info = WorkspaceInfo.from_project_root(tmp_path)

    assert info.python_version == "3.12.0"
    assert info.executable_path == exec_path
    assert info.project_root == tmp_path
    assert info.project_name == "my_project"
    assert info.project_version == "0.1.0"
    assert info.git_branch == "main"
    assert info.latest_commit_hash == "a1b2c3d"
    assert info.git_remote == "https://github.com/user/repo.git"
    assert info.is_venv_active is False
    assert info.package_count == 0
    assert info.packages == []


def test_tomli_import_fallback(monkeypatch):
    dummy_tomli = types.ModuleType("tomli")
    monkeypatch.setitem(sys.modules, "tomli", dummy_tomli)
    monkeypatch.setattr(sys, "version_info", (3, 10, 0, "final, 0"))

    import repopy.info

    importlib.reload(repopy.info)

    assert repopy.info.tomllib is dummy_tomli
