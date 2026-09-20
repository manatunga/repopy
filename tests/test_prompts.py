"""
Automated integration test suite for repopy prompt layout
mapping layers.
"""

from pathlib import Path

import pytest

from repopy.prompts import (
    capture_project_manifests,
    confirm_cleanup,
    confirm_cleanup_artifacts,
    confirm_dependency_installation,
    resolve_unique_project_name,
)


class MockCliArgs:
    def __init__(
        self, project_name=None, theme=None, skip=False, link=None, message=None
    ):
        self.project_name = project_name
        self.theme = theme
        self.skip = skip
        self.link = link
        self.message = message


# -------------------------------------------------------------------------------------
# resolve_unique_project_name Tests
# -------------------------------------------------------------------------------------


def test_resolve_unique_project_name_no_collision(monkeypatch):
    monkeypatch.setattr(Path, "exists", lambda self: False)
    assert resolve_unique_project_name() == "my_python_project"


def test_resolve_unique_project_name_with_collision(monkeypatch):
    calls = []

    def fake_exists(self):
        calls.append(self.name)
        # 'my_python_project' exists, 'my_python_project_1' is free
        return self.name == "my_python_project"

    monkeypatch.setattr(Path, "exists", fake_exists)
    assert resolve_unique_project_name() == "my_python_project_1"


# -------------------------------------------------------------------------------------
# Existing Skip Flag Tests
# -------------------------------------------------------------------------------------


def test_init_with_skip_flag_defaults(monkeypatch):
    monkeypatch.setattr(Path, "exists", lambda self: False)
    simulated_arguments = MockCliArgs(project_name=None, skip=True, theme=None)
    manifest = capture_project_manifests(simulated_arguments)

    assert manifest["project_name"] == "my_python_project"
    assert manifest["theme"] == "minimal"
    assert manifest["version"] == "1.0.0"


def test_init_with_explicit_overrides_and_skip():
    simulated_arguments = MockCliArgs(
        project_name="super_api", theme="web_api", skip=True
    )
    manifest = capture_project_manifests(simulated_arguments)

    assert manifest["project_name"] == "super_api"
    assert manifest["theme"] == "web_api"
    assert manifest["version"] == "1.0.0"


# -------------------------------------------------------------------------------------
# Interactive Name & Theme Prompt Tests
# -------------------------------------------------------------------------------------


def test_capture_manifests_interactive_empty_name_and_default_theme(monkeypatch):
    # User presses Enter for name -> resolve_unique_project_name
    # User presses Enter for theme -> defaults to '1' ('minimal')
    inputs = iter(["", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(Path, "exists", lambda self: False)

    args = MockCliArgs(project_name=None, theme=None, skip=False)
    manifest = capture_project_manifests(args)

    assert manifest["project_name"] == "my_python_project"
    assert manifest["theme"] == "minimal"


def test_capture_manifests_interactive_invalid_name_then_valid(monkeypatch):
    # Invalid name (contains /), then valid name, then theme 'minimal' via '1'
    inputs = iter(["bad/name", "clean_app", "1"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    args = MockCliArgs(project_name=None, theme=None, skip=False)
    manifest = capture_project_manifests(args)

    assert manifest["project_name"] == "clean_app"
    assert manifest["theme"] == "minimal"


def test_capture_manifests_interactive_theme_numeric_retry_and_by_name(monkeypatch):
    # Explicit project_name passed via CLI
    # Theme attempts: invalid digit '9', invalid string 'foo', then valid string 'web_api'
    # Version: '2.1.0', description: 'my desc', author: 'tester'
    inputs = iter(["9", "foo", "web_api", "2.1.0", "my desc", "tester"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    args = MockCliArgs(project_name="my_api", theme=None, skip=False)
    manifest = capture_project_manifests(args)

    assert manifest["project_name"] == "my_api"
    assert manifest["theme"] == "web_api"
    assert manifest["version"] == "2.1.0"
    assert manifest["description"] == "my desc"
    assert manifest["author"] == "tester"


def test_capture_manifests_version_retry_loop_and_whitespace_fields(monkeypatch):
    # Theme '2' ('web_api')
    # Version attempts: invalid 'v1.0-alpha', then Enter (empty string falls back to 1.0.0)
    # Description: whitespace only '   ' -> empty string ''
    # Author: whitespace only '   ' -> empty string ''
    inputs = iter(["2", "v1.0-alpha", "", "   ", "   "])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    args = MockCliArgs(project_name="api_box", theme=None, skip=False)
    manifest = capture_project_manifests(args)

    assert manifest["theme"] == "web_api"
    assert manifest["version"] == "1.0.0"
    assert manifest["description"] == ""
    assert manifest["author"] == ""


# -------------------------------------------------------------------------------------
# Dependency Confirmation Tests
# -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "user_input, expected",
    [
        ("y", True),
        ("yes", True),
        ("Y", True),
        ("n", False),
        ("no", False),
        ("", False),
        ("gibberish", False),
    ],
)
def test_confirm_dependency_responses(monkeypatch, user_input, expected):
    monkeypatch.setattr("builtins.input", lambda _: user_input)
    assert confirm_dependency_installation(["fastapi"]) is expected


def test_confirm_dependency_handles_ctrl_c(monkeypatch):
    monkeypatch.setattr(
        "builtins.input", lambda _: (_ for _ in ()).throw(KeyboardInterrupt)
    )
    assert confirm_dependency_installation(["requests"]) is False


def test_confirm_dependency_handles_eof_error(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(EOFError))
    assert confirm_dependency_installation(["requests"]) is False


# -------------------------------------------------------------------------------------
# Cleanup Confirmation Tests
# -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "user_input, expected",
    [
        ("y", True),
        ("yes", True),
        ("Y", True),
        ("n", False),
        ("no", False),
        ("", False),
        ("gibberish", False),
    ],
)
def test_confirm_cleanup_responses(monkeypatch, user_input, expected):
    monkeypatch.setattr("builtins.input", lambda _: user_input)
    assert confirm_cleanup() is expected


def test_confirm_cleanup_handles_ctrl_c(monkeypatch):
    monkeypatch.setattr(
        "builtins.input", lambda _: (_ for _ in ()).throw(KeyboardInterrupt)
    )
    assert confirm_cleanup() is False


def test_confirm_cleanup_handles_eof_error(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(EOFError))
    assert confirm_cleanup() is False


def test_confirm_cleanup_artifacts_yes(monkeypatch, tmp_path):
    dummy_file = tmp_path / ".coverage"
    monkeypatch.setattr("builtins.input", lambda _: "y")
    assert confirm_cleanup_artifacts([dummy_file]) is True


def test_confirm_cleanup_artifacts_no(monkeypatch, tmp_path):
    dummy_file = tmp_path / ".coverage"
    monkeypatch.setattr("builtins.input", lambda _: "n")
    assert confirm_cleanup_artifacts([dummy_file]) is False


def test_confirm_cleanup_artifacts_interrupt(monkeypatch, tmp_path):
    dummy_file = tmp_path / ".coverage"

    def raise_interrupt(*args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", raise_interrupt)

    result = confirm_cleanup_artifacts([dummy_file])
    assert result is False
