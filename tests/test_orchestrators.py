'''
Automated test suite for repopy's orchestration layer.
'''

from repopy.orchestrators import CloneInitializer
from repopy.git_engine import GitEngine
from repopy.file_system import FileSystemEngine
import repopy.orchestrators as orch

def test_clone_no_install_skips_execution(monkeypatch):
    # Bypasss system checks and validations
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)

    # Bypass disk/network execution
    monkeypatch.setattr(GitEngine, 'clone_repository', lambda self: True)
    monkeypatch.setattr(FileSystemEngine, 'create_virtual_environment', lambda self: True)
    monkeypatch.setattr(FileSystemEngine, 'read_requirements', lambda self: ['requests'])

    installed = False
    def fake_install(self):
        nonlocal installed
        installed = True
        return True

    monkeypatch.setattr(FileSystemEngine, 'install_dependencies', fake_install)

    initializer = CloneInitializer(
        repo_url='https://github.com/user/repo.git',
        dir_name=None,
        install=False,
        no_install=True
    )

    result = initializer.run()
    assert result is True
    assert installed is False


def test_clone_install_triggers_execution(monkeypatch):
    # Bypasss system checks and validations
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)

    # Bypass disk/network execution
    monkeypatch.setattr(GitEngine, 'clone_repository', lambda self: True)
    monkeypatch.setattr(FileSystemEngine, 'create_virtual_environment', lambda self: True)
    monkeypatch.setattr(FileSystemEngine, 'read_requirements', lambda self: ['requests'])

    def fail_if_prompted(*args, **kwargs):
        raise AssertionError('Interactive prompt should not be called when --install is set')

    monkeypatch.setattr(orch, 'confirm_dependency_installation', fail_if_prompted)

    installed = False
    def fake_install(self):
        nonlocal installed
        installed = True
        return True

    monkeypatch.setattr(FileSystemEngine, 'install_dependencies', fake_install)

    initializer = CloneInitializer(
        repo_url='https://github.com/user/repo.git',
        dir_name=None,
        install=True,
        no_install=False
    )

    result = initializer.run()
    assert result is True
    assert installed is True


def test_clone_user_enters_y_triggers_execution(monkeypatch):
    # Bypasss system checks and validations
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)

    # Bypass disk/network execution
    monkeypatch.setattr(GitEngine, 'clone_repository', lambda self: True)
    monkeypatch.setattr(FileSystemEngine, 'create_virtual_environment', lambda self: True)
    monkeypatch.setattr(FileSystemEngine, 'read_requirements', lambda self: ['requests'])
    monkeypatch.setattr(orch, 'confirm_dependency_installation', lambda deps: True)

    installed = False
    def fake_install(self):
        nonlocal installed
        installed = True
        return True

    monkeypatch.setattr(FileSystemEngine, 'install_dependencies', fake_install)

    initializer = CloneInitializer(
        repo_url='https://github.com/user/repo.git',
        dir_name=None,
        install=False,
        no_install=False
    )

    result = initializer.run()
    assert result is True
    assert installed is True


def test_clone_user_enters_n_triggers_execution(monkeypatch):
    # Bypasss system checks and validations
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)

    # Bypass disk/network execution
    monkeypatch.setattr(GitEngine, 'clone_repository', lambda self: True)
    monkeypatch.setattr(FileSystemEngine, 'create_virtual_environment', lambda self: True)
    monkeypatch.setattr(FileSystemEngine, 'read_requirements', lambda self: ['requests'])
    monkeypatch.setattr(orch, 'confirm_dependency_installation', lambda deps: False)

    installed = False
    def fake_install(self):
        nonlocal installed
        installed = True
        return True

    monkeypatch.setattr(FileSystemEngine, 'install_dependencies', fake_install)

    initializer = CloneInitializer(
        repo_url='https://github.com/user/repo.git',
        dir_name=None,
        install=False,
        no_install=False
    )

    result = initializer.run()
    assert result is True
    assert installed is False


def test_clone_no_deps_skips_execution(monkeypatch):
    # Bypasss system checks and validations
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)

    # Bypass disk/network execution
    monkeypatch.setattr(GitEngine, 'clone_repository', lambda self: True)
    monkeypatch.setattr(FileSystemEngine, 'create_virtual_environment', lambda self: True)
    monkeypatch.setattr(FileSystemEngine, 'read_requirements', lambda self: [])

    def fail_if_prompted(*args, **kwargs):
        raise AssertionError('Interactive prompt should not be triggered when deps are empty')

    monkeypatch.setattr(orch, 'confirm_dependency_installation', fail_if_prompted)
    
    installed = False
    def fake_install(self):
        nonlocal installed
        installed = True
        return True

    monkeypatch.setattr(FileSystemEngine, 'install_dependencies', fake_install)

    initializer = CloneInitializer(
        repo_url='https://github.com/user/repo.git',
        dir_name=None,
        install=False,
        no_install=False
    )

    result = initializer.run()
    assert result is True
    assert installed is False