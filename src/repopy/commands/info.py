"""
Command: `repopy info`
"""

from repopy.commands.base import Command
from repopy.orchestrators import InfoInitializer


class InfoCommand(Command):
    name = "info"
    help = "Fetch and display project , git, venv, dependencies and runtime metadata"

    def add_arguments(self, parser):
        parser.add_argument(
            "-j",
            "--json",
            action="store_true",
            help="Output project metadata in JSON format",
        )

    def run(self, args):
        return InfoInitializer(args.json).run()
