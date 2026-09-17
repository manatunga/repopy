'''
Automated test suite for repopy's main entrypoint.
'''

import sys
import pytest

from repopy.__main__ import main

def test_main_init_dispatch(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['repopy', 'init', 'my-app'])
    
    # Supply the expected 'project_name' key
    mock_manifest = {'project_name': 'my-app', 'theme': 'minimal'}
    monkeypatch.setattr('repopy.__main__.capture_project_manifests', lambda args: mock_manifest)

    ran = False
    def fake_run(self):
        nonlocal ran
        ran = True
        return True

    monkeypatch.setattr('repopy.__main__.LocalInitializer.run', fake_run)

    main()
    assert ran is True


def test_main_init_with_link_success(monkeypatch):
    monkeypatch.setattr(
        sys,
        'argv',
        ['repopy', 'init', 'my-app', '--link', 'https://github.com/user/repo.git', '-m', 'Initial']
    )
    mock_manifest = {'project_name': 'my-app', 'theme': 'minimal'}
    monkeypatch.setattr('repopy.__main__.capture_project_manifests', lambda args: mock_manifest)
    monkeypatch.setattr('repopy.__main__.LocalInitializer.run', lambda self: True)

    link_ran = False
    def fake_link_run(self):
        nonlocal link_ran
        link_ran = True
        return True

    monkeypatch.setattr('repopy.__main__.LinkInitializer.run', fake_link_run)

    main()
    assert link_ran is True


def test_main_init_with_link_skipped_on_failure(monkeypatch):
    monkeypatch.setattr(
        sys,
        'argv',
        ['repopy', 'init', 'my-app', '--link', 'https://github.com/user/repo.git']
    )
    mock_manifest = {'project_name': 'my-app', 'theme': 'minimal'}
    monkeypatch.setattr('repopy.__main__.capture_project_manifests', lambda args: mock_manifest)
    # LocalInitializer returns False
    monkeypatch.setattr('repopy.__main__.LocalInitializer.run', lambda self: False)

    def fail_if_link_called(self):
        raise AssertionError('LinkInitializer should not run when LocalInitializer fails')

    monkeypatch.setattr('repopy.__main__.LinkInitializer.run', fail_if_link_called)

    main()


def test_main_clone_dispatch(monkeypatch):
    monkeypatch.setattr(
        sys,
        'argv',
        ['repopy', 'clone', 'https://github.com/user/repo.git', '--no-install']
    )

    clone_ran = False
    def fake_clone_run(self):
        nonlocal clone_ran
        clone_ran = True
        return True

    monkeypatch.setattr('repopy.__main__.CloneInitializer.run', fake_clone_run)

    main()
    assert clone_ran is True


def test_main_link_dispatch(monkeypatch):
    monkeypatch.setattr(
        sys,
        'argv',
        ['repopy', 'link', 'https://github.com/user/repo.git', '-m', 'Initial commit']
    )

    link_ran = False
    def fake_link_run(self):
        nonlocal link_ran
        link_ran = True
        return True

    monkeypatch.setattr('repopy.__main__.LinkInitializer.run', fake_link_run)

    main()
    assert link_ran is True


def test_main_no_subcommand_shows_usage(monkeypatch, capsys):
    # Mock parse_arguments to simulate an args namespace without a recognized command
    class MockArgs:
        command = None

    monkeypatch.setattr('repopy.__main__.parse_arguments', lambda: MockArgs())

    main()
    captured = capsys.readouterr()
    assert 'Usage: repopy [init | clone | link] --help' in captured.out
    assert 'Error: Please specify a subcommand' in captured.out


def test_main_keyboard_interrupt_exits_cleanly(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['repopy', 'init', 'my-app'])

    def fake_interrupt():
        raise KeyboardInterrupt()

    monkeypatch.setattr('repopy.__main__.parse_arguments', fake_interrupt)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert 'Workspace operation cancelled by user.' in captured.out