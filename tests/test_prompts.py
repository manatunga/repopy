'''
Automated integration test suite for repopy prompt layout
mapping layers.
'''

import pytest
from repopy.prompts import capture_project_manifests, confirm_dependency_installation, confirm_cleanup

class MockCliArgs:

    def __init__(self, project_name=None, theme=None, skip=False, link=None, message=None):
        self.project_name = project_name
        self.theme = theme
        self.skip = skip
        self.link = link
        self.message = message


def test_init_with_skip_flag_defaults():
    '''
    Verifies that running `repopy init -s` without passing
    a custom name correctly triggers the automated fallback
    name and the minimal theme layout.
    '''

    simulated_arguments = MockCliArgs(project_name=None, skip=True, theme=None)
    manifest = capture_project_manifests(simulated_arguments)

    assert manifest['project_name'] == 'my_python_project'
    assert manifest['theme'] == 'minimal'
    assert manifest['version'] == '1.0.0'


def test_init_with_explicit_overrides_and_skip():
    '''
    Verifies that running `repopy init [project_name] --theme [theme] --skip`
    completely skips the interactive prompting loop and lock the user-given
    project name and theme into the manifest.
    '''

    simulated_arguments = MockCliArgs(project_name='super_api', theme='web_api', skip=True)
    manifest = capture_project_manifests(simulated_arguments)

    assert manifest['project_name'] == 'super_api'
    assert manifest['theme'] == 'web_api'
    assert manifest['version'] == '1.0.0'


@pytest.mark.parametrize('user_input, expected', [
    ('y', True),
    ('yes', True),
    ('Y', True),
    ('n', False),
    ('no', False),
    ('', False),
    ('gibberish', False)
])
def test_confirm_dependency_responses(monkeypatch, user_input, expected):
    monkeypatch.setattr('builtins.input', lambda _: user_input)
    assert confirm_dependency_installation(['fastapi']) is expected


def test_confirm_dependency_handles_ctrl_c(monkeypatch):
    def raise_interrupt(_):
        raise KeyboardInterrupt

    monkeypatch.setattr('builtins.input', raise_interrupt)
    result = confirm_dependency_installation(['requests'])
    assert result is False

def test_confirm_dependency_handles_eof_error(monkeypatch):
    def raise_eof_error(_):
        raise EOFError

    monkeypatch.setattr('builtins.input', raise_eof_error)
    result = confirm_dependency_installation(['requests'])
    assert result is False


@pytest.mark.parametrize('user_input, expected', [
    ('y', True),
    ('yes', True),
    ('Y', True),
    ('n', False),
    ('no', False),
    ('', False),
    ('gibberish', False)
])
def test_confirm_cleanup_responses(monkeypatch, user_input, expected):
    monkeypatch.setattr('builtins.input', lambda _: user_input)
    assert confirm_cleanup() is expected


def test_confirm_cleanup_handles_ctrl_c(monkeypatch):
    def raise_interrupt(_):
        raise KeyboardInterrupt

    monkeypatch.setattr('builtins.input', raise_interrupt)
    assert confirm_cleanup() is False

def test_confirm_cleanup_handles_eof_error(monkeypatch):
    def raise_eof_error(_):
        raise EOFError

    monkeypatch.setattr('builtins.input', raise_eof_error)
    assert confirm_cleanup() is False