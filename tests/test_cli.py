"""
Automated test suite for repopy cli parser.
"""

import sys
import pytest

from repopy.cli import parse_arguments


def test_clone_defaults(monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["repopy", "clone", "https://github.com/user/repo.git"]
    )
    args = parse_arguments()

    assert args.install is False
    assert args.no_install is False


def test_clone_i_flag(monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["repopy", "clone", "https://github.com/user/repo.git", "-i"]
    )
    args = parse_arguments()

    assert args.install is True
    assert args.no_install is False


def test_clone_install_flag(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["repopy", "clone", "https://github.com/user/repo.git", "--install"],
    )
    args = parse_arguments()

    assert args.install is True
    assert args.no_install is False


def test_clone_no_install_flag(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["repopy", "clone", "https://github.com/user/repo.git", "--no-install"],
    )
    args = parse_arguments()

    assert args.install is False
    assert args.no_install is True


def test_clone_mutual_exclusion(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["repopy", "clone", "https://github.com/user/repo.git", "-i", "--no-install"],
    )

    with pytest.raises(SystemExit):
        parse_arguments()


def test_clean_defaults(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "clean"])
    args = parse_arguments()

    assert args.command == "clean"
    assert args.skip_prompt is False


def test_clean_y_flag(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "clean", "-y"])
    args = parse_arguments()

    assert args.skip_prompt is True


def test_clean_yes_flag(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "clean", "--yes"])
    args = parse_arguments()

    assert args.skip_prompt is True