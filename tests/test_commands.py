"""
Automated test suite for repopy commands entrypoint and registry.
"""

from repopy.commands import COMMANDS


def test_commands_dict_has_all_expected_names():
    expected = {"clean", "clone", "info", "init", "link"}

    assert expected == COMMANDS.keys()


def test_clean_has_required_methods():
    assert hasattr(COMMANDS["clean"], "add_arguments")
    assert hasattr(COMMANDS["clean"], "run")


def test_clone_has_required_methods():
    assert hasattr(COMMANDS["clone"], "add_arguments")
    assert hasattr(COMMANDS["clone"], "run")


def test_info_has_required_methods():
    assert hasattr(COMMANDS["info"], "add_arguments")
    assert hasattr(COMMANDS["info"], "run")


def test_init_has_required_methods():
    assert hasattr(COMMANDS["init"], "add_arguments")
    assert hasattr(COMMANDS["init"], "run")


def test_link_has_required_methods():
    assert hasattr(COMMANDS["link"], "add_arguments")
    assert hasattr(COMMANDS["link"], "run")


def test_command_name_matches_dict_key():
    for key, cmd in COMMANDS.items():
        assert cmd.name == key
