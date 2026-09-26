"""
Automated test suite for repopy's main entrypoint.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

from repopy.__main__ import main


def test_main_init_dispatch(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "init", "my-app"])

    # Supply the expected 'project_name' key
    mock_manifest = {"project_name": "my-app", "theme": "minimal"}
    monkeypatch.setattr(
        "repopy.commands.init.capture_project_manifests", lambda args: mock_manifest
    )

    ran = False

    def fake_run(self):
        nonlocal ran
        ran = True
        return True

    monkeypatch.setattr("repopy.commands.init.LocalInitializer.run", fake_run)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert ran is True
    assert exc_info.value.code == 0


def test_main_init_with_link_success(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "repopy",
            "init",
            "my-app",
            "--link",
            "https://github.com/user/repo.git",
            "-m",
            "Initial",
        ],
    )
    mock_manifest = {"project_name": "my-app", "theme": "minimal"}
    monkeypatch.setattr(
        "repopy.commands.init.capture_project_manifests", lambda args: mock_manifest
    )
    monkeypatch.setattr("repopy.commands.init.LocalInitializer.run", lambda self: True)

    link_ran = False

    def fake_link_run(self):
        nonlocal link_ran
        link_ran = True
        return True

    monkeypatch.setattr("repopy.commands.link.LinkInitializer.run", fake_link_run)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert link_ran is True
    assert exc_info.value.code == 0


def test_main_init_with_link_skipped_on_failure(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["repopy", "init", "my-app", "--link", "https://github.com/user/repo.git"],
    )
    mock_manifest = {"project_name": "my-app", "theme": "minimal"}
    monkeypatch.setattr(
        "repopy.commands.init.capture_project_manifests", lambda args: mock_manifest
    )
    monkeypatch.setattr("repopy.commands.init.LocalInitializer.run", lambda self: False)

    def fail_if_link_called(self):
        raise AssertionError(
            "LinkInitializer should not run when LocalInitializer fails"
        )

    monkeypatch.setattr("repopy.commands.link.LinkInitializer.run", fail_if_link_called)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1


def test_main_clone_dispatch(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["repopy", "clone", "https://github.com/user/repo.git", "--no-install"],
    )

    clone_ran = False

    def fake_clone_run(self):
        nonlocal clone_ran
        clone_ran = True
        return True

    monkeypatch.setattr("repopy.commands.clone.CloneInitializer.run", fake_clone_run)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert clone_ran is True
    assert exc_info.value.code == 0


def test_main_link_dispatch(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["repopy", "link", "https://github.com/user/repo.git", "-m", "Initial commit"],
    )

    link_ran = False

    def fake_link_run(self):
        nonlocal link_ran
        link_ran = True
        return True

    monkeypatch.setattr("repopy.commands.link.LinkInitializer.run", fake_link_run)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert link_ran is True
    assert exc_info.value.code == 0


def test_main_clean_dispatch_success(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "clean", "-y"])
    monkeypatch.setattr("repopy.commands.clean.CleanInitializer.run", lambda self: True)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0


def test_main_clean_dispatch_failure(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "clean"])
    monkeypatch.setattr(
        "repopy.commands.clean.CleanInitializer.run", lambda self: False
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1


def test_main_info_dispatch(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "info"])

    with patch("repopy.commands.info.InfoInitializer") as mock_initializer_cls:
        mock_instance = MagicMock()
        mock_instance.run.return_value = True
        mock_initializer_cls.return_value = mock_instance

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mock_initializer_cls.assert_called_once_with(False)
        mock_instance.run.assert_called_once()


def test_main_info_command_json_flag(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "info", "--json"])

    with patch("repopy.commands.info.InfoInitializer") as mock_initializer_cls:
        mock_instance = MagicMock()
        mock_instance.run.return_value = True
        mock_initializer_cls.return_value = mock_instance

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mock_initializer_cls.assert_called_once_with(True)
        mock_instance.run.assert_called_once()


def test_main_info_command_failure(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["repopy", "info"])

    with patch("repopy.commands.info.InfoInitializer") as mock_initializer_cls:
        mock_instance = MagicMock()
        mock_instance.run.return_value = False
        mock_initializer_cls.return_value = mock_instance

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


def test_main_keyboard_interrupt_exits_cleanly(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["repopy", "init", "my-app"])

    def fake_interrupt():
        raise KeyboardInterrupt()

    monkeypatch.setattr("repopy.__main__.parse_arguments", fake_interrupt)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Workspace operation cancelled by user." in captured.out
