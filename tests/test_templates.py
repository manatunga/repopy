"""
Automated test suite for repopy templates and layouts.
"""

from pathlib import Path

from repopy.info import WorkspaceInfo
from repopy.templates import (
    GITIGNORE_TEMPLATE,
    format_info_output,
    generate_pyproject_toml,
    generate_readme,
)


def test_gitignore_template_content():
    assert "__pycache__/" in GITIGNORE_TEMPLATE
    assert ".venv/" in GITIGNORE_TEMPLATE


def test_generate_readme_output():
    manifest = {"project_name": "sample_project", "description": "A sample CLI tool"}

    readme_output = generate_readme(manifest)

    assert "# sample_project" in readme_output
    assert "A sample CLI tool" in readme_output


def test_generate_pyproject_toml_output():
    manifest = {
        "project_name": "sample_project",
        "version": "0.2.1",
        "description": "A sample CLI tool",
        "author": "Dev Tester",
    }

    toml_output = generate_pyproject_toml(manifest)

    assert "[project]" in toml_output
    assert 'name = "sample_project"' in toml_output
    assert 'version = "0.2.1"' in toml_output
    assert 'description = "A sample CLI tool"' in toml_output
    assert 'name = "Dev Tester"' in toml_output


def test_format_info_output_full():
    info = WorkspaceInfo(
        python_version="3.11.0",
        executable_path="/usr/bin/python3",
        project_root=Path("/tmp/demo"),
        project_name="demo_project",
        project_version="0.1.0",
        is_git_repo=True,
        git_branch="main",
        latest_commit_hash="abc1234",
        git_remote="https://github.com/user/demo.git",
        is_venv_active=True,
        package_count=12,
        packages=["pytest", "requests"],
    )
    output = format_info_output(info)

    assert "demo_project" in output
    assert "0.1.0" in output
    assert "main" in output
    assert "abc1234" in output
    assert "https://github.com/user/demo.git" in output
    assert "12" in output


def test_format_info_output_minimal():
    info = WorkspaceInfo(
        python_version="3.11.0",
        executable_path="/usr/bin/python3",
        project_root=Path("/tmp/demo"),
        project_name=None,
        project_version=None,
        is_git_repo=False,
        git_branch=None,
        latest_commit_hash=None,
        git_remote=None,
        is_venv_active=False,
        package_count=0,
        packages=[],
    )

    output = format_info_output(info)

    # Asserts that fallback branches render cleanly
    assert "Not a Git repository" in output or "N/A" in output
    assert "Status     : Inactive / Not detected" in output