'''
Automated test suite for repopy's OS detection layer.
'''

import platform

from repopy.os_detector import get_os, is_windows, is_mac, is_linux

def test_get_os_windows(monkeypatch):
    monkeypatch.setattr(platform, 'system', lambda: 'Windows')

    assert get_os() == 'windows'
    assert is_windows() is True
    assert is_mac() is False
    assert is_linux() is False


def test_get_os_mac(monkeypatch):
    monkeypatch.setattr(platform, 'system', lambda: 'Darwin')

    assert get_os() == 'mac'
    assert is_windows() is False
    assert is_mac() is True
    assert is_linux() is False


def test_get_os_linux(monkeypatch):
    monkeypatch.setattr(platform, 'system', lambda: 'Linux')

    assert get_os() == 'linux'
    assert is_windows() is False
    assert is_mac() is False
    assert is_linux() is True


def test_get_os_fallback_to_linux(monkeypatch):
    monkeypatch.setattr(platform, 'system', lambda: 'FreeBSD')

    assert get_os() == 'linux'
    assert is_windows() is False
    assert is_mac() is False
    assert is_linux() is True