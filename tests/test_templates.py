'''
Automated test suite for repopy templates and layouts.
'''

from repopy.templates import GITIGNORE_TEMPLATE, generate_pyproject_toml


def test_gitignore_template_content():
    assert '__pycache__/' in GITIGNORE_TEMPLATE
    assert '.venv/' in GITIGNORE_TEMPLATE


def test_generate_pyproject_toml_output():
    manifest = {
        'project_name': 'sample_project',
        'version': '0.2.1',
        'description': 'A sample CLI tool',
        'author': 'Dev Tester',
    }

    toml_output = generate_pyproject_toml(manifest)

    assert '[project]' in toml_output
    assert 'name = "sample_project"' in toml_output
    assert 'version = "0.2.1"' in toml_output
    assert 'description = "A sample CLI tool"' in toml_output
    assert 'name = "Dev Tester"' in toml_output