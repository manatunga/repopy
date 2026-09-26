"""
Command: `repopy clean`
"""

from repopy.commands.base import Command
from repopy.orchestrators import CleanInitializer


class CleanCommand(Command):
    name = "clean"
    help = "Remove transient build, cache and test artifacts"

    def add_arguments(self, parser):
        parser.add_argument(
            "-y",
            "--yes",
            dest="skip_prompt",
            action="store_true",
            help="Skip interactive confirmation prompt",
        )

    def run(self, args):
        print("⌛ Scanning for cleanable artifacts...\n")
        return CleanInitializer(args.skip_prompt).run()
