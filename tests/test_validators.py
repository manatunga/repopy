"""
Automated test suite for repopy validation layers.
"""

from repopy.validators.validators import is_valid_git_url, is_valid_project_name


def test_project_name_validation(tmp_path, monkeypatch):
    # Clean standard string passes
    assert is_valid_project_name("my_cool_python_app") is True

    # Illegal characters fail
    assert is_valid_project_name("bad*folder#name") is False

    # Empty or blank string fails
    assert is_valid_project_name("    ") is False
    assert is_valid_project_name("") is False

    # Existing directory collision fails (covers line 19)
    existing_dir = tmp_path / "already_exists"
    existing_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    assert is_valid_project_name("already_exists") is False


def test_git_url_validation():
    # Valid formats pass
    assert is_valid_git_url("https://github.com/user/repo.git") is True
    assert is_valid_git_url("https://github.com/user/repo.git/") is True
    assert is_valid_git_url("git@github.com:user/repo.git") is True

    # Incomplete git URLs fail
    assert is_valid_git_url("https://github.com/user/repo") is False
    assert is_valid_git_url("https://.com/user/repo.git") is False
    assert is_valid_git_url("github.com:user/repo.git") is False

    # Non-GitHub SSH hosts fail (covers line 30)
    assert is_valid_git_url("git@gitlab.com:user/repo.git") is False

    # Path segment edge cases (covers line 51)
    assert is_valid_git_url("https://github.com/.git") is False
    assert is_valid_git_url("https://github.com/repo.git") is False
    assert is_valid_git_url("git@github.com:repo.git") is False

    # Outright illegal strings fail
    assert is_valid_git_url("") is False
    assert is_valid_git_url("   ") is False
    assert is_valid_git_url("just-a-plain-string") is False
    assert is_valid_git_url("/Users/desktop/my_project/.git") is False


def test_git_url_ssh_split_error(monkeypatch):
    # Covers lines 33-34 ValueError handler
    # A string that passes startswith('git@github.com:') but fails split(':', 1)
    class MalformedSshStr(str):
        def startswith(self, prefix, *args):
            return True

        def split(self, sep=None, maxsplit=-1):
            raise ValueError("simulated split error")

    assert is_valid_git_url(MalformedSshStr("git@github.com:dummy")) is False
