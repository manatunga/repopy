"""
Automated test suite for repopy cli parser.
"""

import sys

import pytest

from repopy.ui.cli import parse_arguments


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


def test_info_defaults(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "info"])
    args = parse_arguments()

    assert args.command == "info"
    assert args.json is False


def test_info_j_flag(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "info", "-j"])
    args = parse_arguments()

    assert args.json is True


def test_info_json_flag(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "info", "--json"])
    args = parse_arguments()

    assert args.json is True


def test_link_defaults(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["repopy", "link", "https://github.com/user/repo.git"]
    )
    args = parse_arguments()

    assert args.command == "link"
    assert args.repo_url == "https://github.com/user/repo.git"
    assert args.message is None


def test_link_m_flag(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["repopy", "link", "https://github.com/user/repo.git", "-m", "First commit"]
    )
    args = parse_arguments()

    assert args.message == "First commit"


def test_link_message_flag(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["repopy", "link", "https://github.com/user/repo.git", "--message", "First commit"]
    )
    args = parse_arguments()

    assert args.message == "First commit"


def test_link_missing_repo_url(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "link"])

    with pytest.raises(SystemExit):
        parse_arguments()


def test_init_defaults(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "init"])
    args = parse_arguments()

    assert args.project_name is None
    assert args.theme is None
    assert args.skip is False
    assert args.link is None
    assert args.message is None


def test_init_with_project_name(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "init", "my-app"])
    args = parse_arguments()

    assert args.project_name == "my-app"
    assert args.theme is None
    assert args.skip is False
    assert args.link is None
    assert args.message is None


def test_init_with_valid_theme(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "init", "-t", "web_api"])
    args = parse_arguments()

    assert args.project_name is None
    assert args.theme == "web_api"
    assert args.skip is False
    assert args.link is None
    assert args.message is None


def test_init_with_invalid_theme(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "init", "-t", "my_app"])

    with pytest.raises(SystemExit):
        parse_arguments()


def test_init_with_skip_flag(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "init", "-s"])
    args = parse_arguments()

    assert args.project_name is None
    assert args.theme is None
    assert args.skip is True
    assert args.link is None
    assert args.message is None


def test_init_with_link_and_message_flags(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["repopy", "init", "-l", "https://github.com/user/repo.git", "-m", "First commit"]
    )
    args = parse_arguments()

    assert args.project_name is None
    assert args.theme is None
    assert args.skip is False
    assert args.link == "https://github.com/user/repo.git"
    assert args.message == "First commit"
