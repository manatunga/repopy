'''
Automated test suite for repopy's file system engine.
'''

import subprocess
import venv
from pathlib import Path

from repopy.file_system import FileSystemEngine

#-------------------------------------------------------------------------------------
# Existing Requirements Parsing Tests
#-------------------------------------------------------------------------------------

def test_read_requirements_filters_comments_and_blanks(tmp_path):
    req_file = tmp_path / 'requirements.txt'
    req_file.write_text('requests>=2.28\n\n# comment\npytest\n    \n')

    fs_engine = FileSystemEngine(tmp_path)
    deps = fs_engine.read_requirements()

    assert deps == ['requests>=2.28', 'pytest']


def test_read_requirements_missing_file(tmp_path):
    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.read_requirements() == []


def test_read_requirements_empty_file(tmp_path):
    req_file = tmp_path / 'requirements.txt'
    req_file.write_text('')

    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.read_requirements() == []


#-------------------------------------------------------------------------------------
# Root Directory & Theme Structure
#-------------------------------------------------------------------------------------

def test_create_root_directory_success(tmp_path):
    target = tmp_path / 'new_project'
    fs_engine = FileSystemEngine(target)
    assert fs_engine.create_root_directory() is True
    assert target.is_dir()


def test_create_root_directory_failure(monkeypatch, tmp_path):
    fs_engine = FileSystemEngine(tmp_path / 'fail_dir')

    def fake_mkdir(*args, **kwargs):
        raise OSError('Permission denied')

    monkeypatch.setattr(Path, 'mkdir', fake_mkdir)
    assert fs_engine.create_root_directory() is False


def test_create_theme_directories_web_api(tmp_path):
    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.create_theme_directories('web_api', 'my_api') is True
    assert (tmp_path / 'src/app/routes').is_dir()
    assert (tmp_path / 'src/app/models').is_dir()


def test_create_theme_directories_cli_package(tmp_path):
    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.create_theme_directories('cli_package', 'my_pkg') is True
    assert (tmp_path / 'src/my_pkg').is_dir()
    assert (tmp_path / 'tests').is_dir()


def test_create_theme_directories_data_science(tmp_path):
    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.create_theme_directories('data_science', 'ds_proj') is True
    assert (tmp_path / 'data/raw').is_dir()
    assert (tmp_path / 'data/processed').is_dir()
    assert (tmp_path / 'notebooks').is_dir()
    assert (tmp_path / 'src/pipeline').is_dir()


def test_create_theme_directories_unknown_or_minimal(tmp_path):
    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.create_theme_directories('minimal', 'min_proj') is True


def test_create_theme_directories_failure(monkeypatch, tmp_path):
    fs_engine = FileSystemEngine(tmp_path)

    def fake_mkdir(*args, **kwargs):
        raise OSError('Disk write failure')

    monkeypatch.setattr(Path, 'mkdir', fake_mkdir)
    assert fs_engine.create_theme_directories('web_api', 'my_api') is False


#-------------------------------------------------------------------------------------
# Theme Configurations (Templates)
#-------------------------------------------------------------------------------------

def test_write_theme_configurations_minimal(tmp_path):
    fs_engine = FileSystemEngine(tmp_path)
    manifest = {'project_name': 'test_min', 'author': 'tester'}
    assert fs_engine.write_theme_configurations('minimal', manifest) is True
    assert (tmp_path / '.gitignore').is_file()
    assert (tmp_path / 'README.md').is_file()
    assert (tmp_path / 'requirements.txt').is_file()
    assert (tmp_path / 'requirements.txt').read_text() == ''


def test_write_theme_configurations_pyproject_toml(monkeypatch, tmp_path):
    fs_engine = FileSystemEngine(tmp_path)
    monkeypatch.setattr(
        'repopy.file_system.generate_pyproject_toml',
        lambda manifest: '[project]\nname = "test_pkg"\n'
    )
    manifest = {'project_name': 'test_pkg'}
    assert fs_engine.write_theme_configurations('cli_package', manifest) is True
    assert (tmp_path / 'pyproject.toml').is_file()
    assert '[project]' in (tmp_path / 'pyproject.toml').read_text()


def test_write_theme_configurations_failure(monkeypatch, tmp_path):
    fs_engine = FileSystemEngine(tmp_path)

    def fake_open(*args, **kwargs):
        raise OSError('Cannot open file')

    monkeypatch.setattr('builtins.open', fake_open)
    assert fs_engine.write_theme_configurations('minimal', {}) is False


#-------------------------------------------------------------------------------------
# Virtual Environment Creation
#-------------------------------------------------------------------------------------

def test_create_virtual_environment_success(monkeypatch, tmp_path):
    created = []

    def fake_create(env_dir, with_pip=True):
        created.append((env_dir, with_pip))

    monkeypatch.setattr(venv, 'create', fake_create)
    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.create_virtual_environment() is True
    assert created == [(tmp_path / '.venv', True)]


def test_create_virtual_environment_failure(monkeypatch, tmp_path):
    def fake_create(env_dir, with_pip=True):
        raise RuntimeError('Venv creation failed')

    monkeypatch.setattr(venv, 'create', fake_create)
    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.create_virtual_environment() is False


#-------------------------------------------------------------------------------------
# Git Initialization
#-------------------------------------------------------------------------------------

def test_initialize_git_success(monkeypatch, tmp_path):
    def fake_run(cmd, cwd, capture_output, text):
        assert cmd == ['git', 'init']
        assert cwd == tmp_path
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout='', stderr='')

    monkeypatch.setattr(subprocess, 'run', fake_run)
    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.initialize_git() is True


def test_initialize_git_nonzero_exit(monkeypatch, tmp_path):
    def fake_run(cmd, cwd, capture_output, text):
        return subprocess.CompletedProcess(args=cmd, returncode=1, stdout='', stderr='git error')

    monkeypatch.setattr(subprocess, 'run', fake_run)
    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.initialize_git() is False


def test_initialize_git_os_error(monkeypatch, tmp_path):
    def fake_run(*args, **kwargs):
        raise OSError('git executable not found')

    monkeypatch.setattr(subprocess, 'run', fake_run)
    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.initialize_git() is False


#-------------------------------------------------------------------------------------
# Dependency Installation
#-------------------------------------------------------------------------------------

def test_install_dependencies_no_requirements_file(tmp_path):
    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.install_dependencies() is True


def test_install_dependencies_posix_success(monkeypatch, tmp_path):
    req_file = tmp_path / 'requirements.txt'
    req_file.write_text('pytest\n')

    monkeypatch.setattr('repopy.file_system.is_windows', lambda: False)

    executed_cmd = []

    def fake_run(cmd, capture_output, text):
        executed_cmd.append(cmd)
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout='', stderr='')

    monkeypatch.setattr(subprocess, 'run', fake_run)
    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.install_dependencies() is True
    assert executed_cmd[0] == [str(tmp_path / '.venv' / 'bin' / 'pip'), 'install', '-r', str(req_file)]


def test_install_dependencies_windows_success(monkeypatch, tmp_path):
    req_file = tmp_path / 'requirements.txt'
    req_file.write_text('pytest\n')

    monkeypatch.setattr('repopy.file_system.is_windows', lambda: True)

    executed_cmd = []

    def fake_run(cmd, capture_output, text):
        executed_cmd.append(cmd)
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout='', stderr='')

    monkeypatch.setattr(subprocess, 'run', fake_run)
    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.install_dependencies() is True
    assert executed_cmd[0] == [str(tmp_path / '.venv' / 'Scripts' / 'pip.exe'), 'install', '-r', str(req_file)]


def test_install_dependencies_failure_exit_code(monkeypatch, tmp_path):
    req_file = tmp_path / 'requirements.txt'
    req_file.write_text('pytest\n')

    monkeypatch.setattr('repopy.file_system.is_windows', lambda: False)
    monkeypatch.setattr(
        subprocess,
        'run',
        lambda *args, **kwargs: subprocess.CompletedProcess(args=[], returncode=1)
    )

    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.install_dependencies() is False


def test_install_dependencies_os_error(monkeypatch, tmp_path):
    req_file = tmp_path / 'requirements.txt'
    req_file.write_text('pytest\n')

    def fake_run(*args, **kwargs):
        raise OSError('Pip execution failed')

    monkeypatch.setattr(subprocess, 'run', fake_run)
    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.install_dependencies() is False


#-------------------------------------------------------------------------------------
# Activation Guide
#-------------------------------------------------------------------------------------

def test_get_activation_guide_posix(monkeypatch, tmp_path):
    monkeypatch.setattr('repopy.file_system.is_windows', lambda: False)
    fs_engine = FileSystemEngine(tmp_path)
    guide = fs_engine.get_activation_guide()
    assert 'source .venv/bin/activate' in guide
    assert str(tmp_path) in guide


def test_get_activation_guide_windows(monkeypatch, tmp_path):
    monkeypatch.setattr('repopy.file_system.is_windows', lambda: True)
    fs_engine = FileSystemEngine(tmp_path)
    guide = fs_engine.get_activation_guide()
    assert 'Activate.ps1' in guide
    assert 'activate.bat' in guide


#-------------------------------------------------------------------------------------
# Cleanup / Rollback
#-------------------------------------------------------------------------------------

def test_cleanup_existing_directory(tmp_path):
    target = tmp_path / 'dirty_dir'
    target.mkdir()
    (target / 'partial_file.txt').write_text('data')

    fs_engine = FileSystemEngine(target)
    fs_engine.cleanup()
    assert not target.exists()


def test_cleanup_nonexistent_directory(tmp_path):
    target = tmp_path / 'does_not_exist'
    fs_engine = FileSystemEngine(target)
    fs_engine.cleanup()  # Should complete without error


def test_cleanup_handles_os_error(monkeypatch, tmp_path):
    target = tmp_path / 'locked_dir'
    target.mkdir()

    def fake_rmtree(path):
        raise OSError('Directory locked')

    monkeypatch.setattr('shutil.rmtree', fake_rmtree)
    fs_engine = FileSystemEngine(target)
    fs_engine.cleanup()  # Should catch error and log without raising


#-------------------------------------------------------------------------------------
# build_workspace Pipeline
#-------------------------------------------------------------------------------------

def test_build_workspace_success(monkeypatch, tmp_path):
    fs_engine = FileSystemEngine(tmp_path)
    monkeypatch.setattr(fs_engine, 'create_root_directory', lambda: True)
    monkeypatch.setattr(fs_engine, 'initialize_git', lambda: True)
    monkeypatch.setattr(fs_engine, 'create_theme_directories', lambda t, n: True)
    monkeypatch.setattr(fs_engine, 'write_theme_configurations', lambda t, m: True)
    monkeypatch.setattr(fs_engine, 'create_virtual_environment', lambda: True)

    assert fs_engine.build_workspace('minimal', {'project_name': 'test'}) is True


def test_build_workspace_short_circuits_on_failure(monkeypatch, tmp_path):
    fs_engine = FileSystemEngine(tmp_path)
    monkeypatch.setattr(fs_engine, 'create_root_directory', lambda: True)
    monkeypatch.setattr(fs_engine, 'initialize_git', lambda: False)

    assert fs_engine.build_workspace('minimal', {'project_name': 'test'}) is False