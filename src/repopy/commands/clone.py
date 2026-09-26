"""
Command: `repopy clone`
"""

from repopy.commands.base import Command
from repopy.orchestrators import CloneInitializer


class CloneCommand(Command):
    name = "clone"
    help = "Clones a remote Git repository to the local machine"

    def add_arguments(self, parser):
        parser.add_argument(
            "repo_url",
            help="Repository URL from Github to clone locally (e.g., git@github.com:user/repo.git)",
        )
        parser.add_argument("-n", "--name", help="Name of the project folder")
        deps_group = parser.add_mutually_exclusive_group()
        deps_group.add_argument(
            "-i",
            "--install",
            action="store_true",
            help="Automatically install dependencies without confirmation",
        )
        deps_group.add_argument(
            "--no-install",
            action="store_true",
            help="Skip dependency installation completely (fetch-only safe mode)",
        )

    def run(self, args):
        print("⌛ Cloning remote repository...\n")
        return CloneInitializer(
            args.repo_url, args.name, args.install, args.no_install
        ).run()
