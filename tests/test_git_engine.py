'''
Automated test suite for repopy's git engine.
'''

import subprocess
from pathlib import Path
from repopy.git_engine import GitEngine, GitLinkEngine


def test_git_engine_path_derivation_default():
    engine = GitEngine('https://github.com/user/demo-repo.git', dir_name=None)
    assert engine.project_path == Path('demo-repo')


def test_git_engine_path_derivation_custom_name():
    engine = GitEngine('https://github.com/user/demo-repo.git', dir_name='my_custom_dir')
    assert engine.project_path == Path('my_custom_dir')


def test_clone_repository_success(monkeypatch):
    def fake_run(cmd, *args, **kwargs):
        assert cmd == ['git', 'clone', 'https://github.com/user/repo.git', 'repo']
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout='', stderr='')

    monkeypatch.setattr(subprocess, 'run', fake_run)

    engine = GitEngine('https://github.com/user/repo.git', dir_name=None)
    assert engine.clone_repository() is True


def test_clone_repository_failure_exit_code(monkeypatch):
    def fake_run(cmd, *args, **kwargs):
        return subprocess.CompletedProcess(args=cmd, returncode=128, stdout='', stderr='Fatal error')

    monkeypatch.setattr(subprocess, 'run', fake_run)

    engine = GitEngine('https://github.com/user/repo.git', dir_name=None)
    assert engine.clone_repository() is False


def test_clone_repository_handles_os_error(monkeypatch):
    def fake_run(*args, **kwargs):
        raise OSError('git executable missing or broken pipe')

    monkeypatch.setattr(subprocess, 'run', fake_run)

    engine = GitEngine('https://github.com/user/repo.git', dir_name=None)
    assert engine.clone_repository() is False


def test_git_link_engine_success(monkeypatch):
    executed_commands = []

    def fake_run(cmd, *args, **kwargs):
        executed_commands.append(cmd)
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout='')

    monkeypatch.setattr(subprocess, 'run', fake_run)

    engine = GitLinkEngine('https://github.com/user/demo.git', 'feat: initial commit')
    assert engine.link_and_push() is True
    assert len(executed_commands) == 5
    assert executed_commands[1] == ['git', 'commit', '-m', 'feat: initial commit']
    assert executed_commands[3] == ['git', 'remote', 'add', 'origin', 'https://github.com/user/demo.git']


def test_git_link_nothing_to_commit(monkeypatch):
    executed_commands = []

    def fake_run(cmd, *args, **kwargs):
        executed_commands.append(cmd)
        if cmd[1] == 'commit':
            return subprocess.CompletedProcess(args=cmd, returncode=1, stdout='nothing to commit')
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout='')

    monkeypatch.setattr(subprocess, 'run', fake_run)

    engine = GitLinkEngine('https://github.com/user/repo.git', 'feat: initial commit')
    assert engine.link_and_push() is True
    assert len(executed_commands) == 5


def test_git_link_early_abort_on_failure(monkeypatch):
    executed_commands = []

    def fake_run(cmd, *args, **kwargs):
        executed_commands.append(cmd)
        if cmd[1] == 'remote':
            return subprocess.CompletedProcess(args=cmd, returncode=128, stdout='remote already exists')
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout='')

    monkeypatch.setattr(subprocess, 'run', fake_run)

    engine = GitLinkEngine('https://github.com/user/repo.git', 'feat: initial commit')
    assert engine.link_and_push() is False
    assert len(executed_commands) == 4


def test_git_link_handles_os_error(monkeypatch):
    def fake_run(*args, **kwargs):
        raise OSError('git executable missing or broken pipe')

    monkeypatch.setattr(subprocess, 'run', fake_run)

    engine = GitLinkEngine('https://github.com/user/repo.git', 'feat: initial commit')
    assert engine.link_and_push() is False


def test_git_link_stage_failure(monkeypatch):
    def fake_run(cmd, *args, **kwargs):
        if cmd[1] == 'add':
            return subprocess.CompletedProcess(args=cmd, returncode=1, stderr='stage error')
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    monkeypatch.setattr(subprocess, 'run', fake_run)
    engine = GitLinkEngine('https://github.com/user/repo.git', 'init')
    assert engine.link_and_push() is False


def test_git_link_commit_real_failure(monkeypatch):
    def fake_run(cmd, *args, **kwargs):
        if cmd[1] == 'commit':
            return subprocess.CompletedProcess(args=cmd, returncode=1, stdout='author identity unknown')
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    monkeypatch.setattr(subprocess, 'run', fake_run)
    engine = GitLinkEngine('https://github.com/user/repo.git', 'init')
    assert engine.link_and_push() is False


def test_git_link_branch_failure(monkeypatch):
    def fake_run(cmd, *args, **kwargs):
        if cmd[1] == 'branch':
            return subprocess.CompletedProcess(args=cmd, returncode=1, stderr='branch error')
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    monkeypatch.setattr(subprocess, 'run', fake_run)
    engine = GitLinkEngine('https://github.com/user/repo.git', 'init')
    assert engine.link_and_push() is False


def test_git_link_push_failure(monkeypatch):
    def fake_run(cmd, *args, **kwargs):
        if cmd[1] == 'push':
            return subprocess.CompletedProcess(args=cmd, returncode=1, stderr='remote rejected')
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    monkeypatch.setattr(subprocess, 'run', fake_run)
    engine = GitLinkEngine('https://github.com/user/repo.git', 'init')
    assert engine.link_and_push() is False