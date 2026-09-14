'''
Validation layer. Checks the validity of positional arguments
for both `repopy local` and `repopy clone`.
'''

from pathlib import Path
from urllib.parse import urlsplit

def is_valid_project_name(name: str) -> bool:
    if not name or name.strip() == '':
        return False

    illegal_chars = {'<', '>', '/', '\\', ':', '*', '?', '"', '|', '!', '#'}
    if not illegal_chars.isdisjoint(name):
        return False

    target_path = Path(name)
    if target_path.is_dir():
        return False

    return True


def is_valid_git_url(url: str) -> bool:
    if not url or not url.strip():
        return False

    if url.startswith('git@'):
        if not url.startswith('git@github.com:'):
            return False
        try:
            _, path = url.split(':', 1)
        except ValueError:
            return False

    elif url.startswith(('https://', 'http://')):
        if not url.startswith('https://github.com'):
            return False
        path = urlsplit(url).path

    else:
        return False

    cleaned_path = path.rstrip('/')

    if not cleaned_path.endswith('.git'):
        return False

    path_segments = [seg for seg in cleaned_path.split('/') if seg]
    if len(path_segments) < 2 or path_segments[-1] == '.git':
        return False

    return True