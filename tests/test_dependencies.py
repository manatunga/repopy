"""
Automated test suite for repopy's dependency detection layer.
"""

import shutil

from repopy.validators.dependencies import has_git, has_python


def test_has_python_found(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda cmd: "/usr/bin/python3")
    assert has_python() is True


def test_has_python_missing(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda cmd: None)
    assert has_python() is False


def test_has_git_found(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda cmd: "/usr/bin/git")
    assert has_git() is True


def test_has_git_missing(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda cmd: None)
    assert has_git() is False
