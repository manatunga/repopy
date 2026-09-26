"""
Command: `repopy link`
"""

from repopy.commands.base import Command
from repopy.orchestrators import LinkInitializer


class LinkCommand(Command):
    name = "link"
    help = "Stage, commit and link current local repository to a remote Git URL"

    def add_arguments(self, parser):
        parser.add_argument(
            "repo_url",
            help="Target remote Git repository URL (e.g., git@github.com:user/repo.git)",
        )
        parser.add_argument(
            "-m",
            "--message",
            help="Custom commit message to use instead of the default repopy message",
        )

    def run(self, args):
        print("\n⌛ Linking project to remote endpoint...\n")
        return LinkInitializer(args.repo_url, args.message).run()
