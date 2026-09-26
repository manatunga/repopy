"""
Main entrypoint of repopy. Brings together the argument parser and
the orchestrators together under a main function.
"""

import sys

from repopy.commands import COMMANDS
from repopy.ui.cli import parse_arguments


def main() -> None:
    try:
        args = parse_arguments()
        success = COMMANDS[args.command].run(args)
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n ✖️ Workspace operation cancelled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
