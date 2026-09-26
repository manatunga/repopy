"""
Parser layer. Imports Python's built-in argparse module
to identify user intent and any extra information passed.
"""

import argparse

from repopy.commands import COMMANDS


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="repopy: A modular project scaffolder and workflow manager for Python."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for cmd in COMMANDS.values():
        cmd_parser = subparsers.add_parser(cmd.name, help=cmd.help)
        cmd.add_arguments(cmd_parser)

    return parser.parse_args()
