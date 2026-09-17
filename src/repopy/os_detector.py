'''
OS Detection layer. Contains the importable logic required to
find the local machine's underlying operating system.
'''

import platform


def get_os() -> str:
    system = platform.system()

    if system == 'Windows':
        return 'windows'
    if system == 'Darwin':
        return 'mac'

    return 'linux'

def is_windows() -> bool:
    return get_os() == 'windows'

def is_mac() -> bool:
    return get_os() == 'mac'

def is_linux() -> bool:
    return get_os() == 'linux'