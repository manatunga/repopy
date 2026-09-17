'''
Layer for Dependency-checking. Contains functions to check whether
expected dependencies (such as python and git) are installed.
'''

import shutil


def has_python() -> bool:
    return bool(shutil.which('python') or shutil.which('python3'))


def has_git() -> bool:
    return bool(shutil.which('git'))