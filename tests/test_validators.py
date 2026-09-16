'''
Automated test suite for repopy validation layers.
'''

from repopy.validators import is_valid_project_name, is_valid_git_url

def test_project_name_validation():
    '''
    Verifies that the folder name validation engine correctly filters safe
    inputs from illegal or conflicting naming patterns.
    '''

    # Target check A: Clean, standard string should pass flawlessly
    assert is_valid_project_name('my_cool_python_app') is True

    # Target check B: A name containing illegal characters must fail
    assert is_valid_project_name('bad*folder#name') is False

    # Target check C: An empty or blank input string must fail
    assert is_valid_project_name('    ') is False


def test_git_url_validation():
    '''
    Verifies that the remote git URL validation engine correctly filters
    valid GitHub URL from incomplete URLs or illegal srting layout.
    '''

    # Target check A: A valid, complete git URL should pass flawlessly
    assert is_valid_git_url('https://github.com/user/repo.git') is True
    assert is_valid_git_url('git@github.com:user/repo.git') is True

    # Target check B: An incomplete git URL formats must fail
    assert is_valid_git_url('https://github.com/user/repo') is False
    assert is_valid_git_url('https://.com/user/repo.git') is False
    assert is_valid_git_url('github.com:user/repo.git') is False

    # Target check C: Outright illegal strings (non-URLs) must fail
    assert is_valid_git_url('   ') is False
    assert is_valid_git_url('just-a-plain-string') is False
    assert is_valid_git_url('/Users/desktop/my_project/.git') is False