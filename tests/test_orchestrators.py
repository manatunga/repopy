'''
Automated test suite for repopy's orchestration layer.
'''

from pathlib import Path
from repopy.orchestrators import LocalInitializer, CloneInitializer, LinkInitializer
from repopy.git_engine import GitEngine, GitLinkEngine
from repopy.file_system import FileSystemEngine
import repopy.orchestrators as orch


#-------------------------------------------------------------------------------------
# LocalInitializer Tests
#-------------------------------------------------------------------------------------

def test_local_initializer_missing_python(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: False)
    initializer = LocalInitializer({'project_name': 'test_app', 'theme': 'minimal'})
    assert initializer.run() is False


def test_local_initializer_invalid_name(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: False)
    initializer = LocalInitializer({'project_name': 'invalid*name', 'theme': 'minimal'})
    assert initializer.run() is False


def test_local_initializer_success(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)
    monkeypatch.setattr(FileSystemEngine, 'build_workspace', lambda self, theme, manifest: True)
    monkeypatch.setattr(FileSystemEngine, 'get_activation_guide', lambda self: 'Activate guide')

    initializer = LocalInitializer({'project_name': 'my_app', 'theme': 'minimal'})
    assert initializer.run() is True


def test_local_initializer_build_failure_triggers_cleanup(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)
    monkeypatch.setattr(FileSystemEngine, 'build_workspace', lambda self, theme, manifest: False)

    cleaned = False

    def fake_cleanup(self):
        nonlocal cleaned
        cleaned = True

    monkeypatch.setattr(FileSystemEngine, 'cleanup', fake_cleanup)

    initializer = LocalInitializer({'project_name': 'fail_app', 'theme': 'minimal'})
    assert initializer.run() is False
    assert cleaned is True


#-------------------------------------------------------------------------------------
# CloneInitializer Tests
#-------------------------------------------------------------------------------------

def test_clone_no_install_skips_execution(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)

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
        no_install=True,
    )

    result = initializer.run()
    assert result is True
    assert installed is False


def test_clone_install_triggers_execution(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)

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
        no_install=False,
    )

    result = initializer.run()
    assert result is True
    assert installed is True


def test_clone_user_enters_y_triggers_execution(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)

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
        no_install=False,
    )

    result = initializer.run()
    assert result is True
    assert installed is True


def test_clone_user_enters_n_triggers_execution(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)

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
        no_install=False,
    )

    result = initializer.run()
    assert result is True
    assert installed is False


def test_clone_no_deps_skips_execution(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)

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
        no_install=False,
    )

    result = initializer.run()
    assert result is True
    assert installed is False


def test_clone_missing_host_tools(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: False)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    initializer = CloneInitializer('https://github.com/user/repo.git', None, False, False)
    assert initializer.run() is False


def test_clone_invalid_git_url(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: False)

    initializer = CloneInitializer('not-a-valid-url', None, False, False)
    assert initializer.run() is False


def test_clone_invalid_derived_dir_name(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: False)

    initializer = CloneInitializer('https://github.com/user/repo.git', 'invalid*name', False, False)
    assert initializer.run() is False


def test_clone_git_clone_failure(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)
    monkeypatch.setattr(GitEngine, 'clone_repository', lambda self: False)

    initializer = CloneInitializer('https://github.com/user/repo.git', None, False, False)
    assert initializer.run() is False


def test_clone_venv_creation_failure_triggers_cleanup(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)
    monkeypatch.setattr(GitEngine, 'clone_repository', lambda self: True)
    monkeypatch.setattr(FileSystemEngine, 'create_virtual_environment', lambda self: False)

    cleaned = False

    def fake_cleanup(self):
        nonlocal cleaned
        cleaned = True

    monkeypatch.setattr(FileSystemEngine, 'cleanup', fake_cleanup)

    initializer = CloneInitializer('https://github.com/user/repo.git', None, False, False)
    assert initializer.run() is False
    assert cleaned is True


def test_clone_pip_install_failure_user_approves_cleanup(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)
    monkeypatch.setattr(GitEngine, 'clone_repository', lambda self: True)
    monkeypatch.setattr(FileSystemEngine, 'create_virtual_environment', lambda self: True)
    monkeypatch.setattr(FileSystemEngine, 'read_requirements', lambda self: ['requests'])
    monkeypatch.setattr(FileSystemEngine, 'install_dependencies', lambda self: False)
    monkeypatch.setattr(orch, 'confirm_cleanup', lambda: True)

    cleaned = False

    def fake_cleanup(self):
        nonlocal cleaned
        cleaned = True

    monkeypatch.setattr(FileSystemEngine, 'cleanup', fake_cleanup)

    initializer = CloneInitializer('https://github.com/user/repo.git', None, install=True, no_install=False)
    assert initializer.run() is False
    assert cleaned is True


def test_clone_pip_install_failure_user_declines_cleanup(monkeypatch):
    monkeypatch.setattr(orch, 'has_python', lambda: True)
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(orch, 'is_valid_git_url', lambda _: True)
    monkeypatch.setattr(orch, 'is_valid_project_name', lambda _: True)
    monkeypatch.setattr(GitEngine, 'clone_repository', lambda self: True)
    monkeypatch.setattr(FileSystemEngine, 'create_virtual_environment', lambda self: True)
    monkeypatch.setattr(FileSystemEngine, 'read_requirements', lambda self: ['requests'])
    monkeypatch.setattr(FileSystemEngine, 'install_dependencies', lambda self: False)
    monkeypatch.setattr(orch, 'confirm_cleanup', lambda: False)

    initializer = CloneInitializer('https://github.com/user/repo.git', None, install=True, no_install=False)
    assert initializer.run() is True


#-------------------------------------------------------------------------------------
# LinkInitializer Tests
#-------------------------------------------------------------------------------------

def test_link_missing_git(monkeypatch):
    monkeypatch.setattr(orch, 'has_git', lambda: False)
    initializer = LinkInitializer('https://github.com/user/repo.git', message=None)
    assert initializer.run() is False


def test_link_missing_local_git_repo(monkeypatch):
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(Path, 'exists', lambda self: False)
    initializer = LinkInitializer('https://github.com/user/repo.git', message=None)
    assert initializer.run() is False


def test_link_success_with_default_message(monkeypatch):
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(Path, 'exists', lambda self: True)
    monkeypatch.setattr(GitLinkEngine, 'link_and_push', lambda self: True)

    initializer = LinkInitializer('https://github.com/user/repo.git', message=None)
    assert initializer.message == 'Initial commit: Workspace structured by repopy'
    assert initializer.run() is True


def test_link_failure(monkeypatch):
    monkeypatch.setattr(orch, 'has_git', lambda: True)
    monkeypatch.setattr(Path, 'exists', lambda self: True)
    monkeypatch.setattr(GitLinkEngine, 'link_and_push', lambda self: False)

    initializer = LinkInitializer('https://github.com/user/repo.git', message='Custom message')
    assert initializer.run() is False