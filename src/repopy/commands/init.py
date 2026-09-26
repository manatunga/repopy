"""
Command: `repopy init`
"""

from repopy.commands.base import Command
from repopy.orchestrators import LinkInitializer, LocalInitializer
from repopy.prompts import capture_project_manifests


class InitCommand(Command):
    name = "init"
    help = "Initializes a standardized Python development workspace in a new directory"

    def add_arguments(self, parser):
        parser.add_argument(
            "project_name",
            nargs="?",
            help="Name of the target project folder to create",
        )
        parser.add_argument(
            "-t",
            "--theme",
            choices=["minimal", "web_api", "cli_package", "data_science"],
            help="Pre-select an architectural theme layout",
        )
        parser.add_argument(
            "-s",
            "--skip",
            action="store_true",
            help="Skip interactive loops and generate workspace using default values",
        )
        parser.add_argument(
            "-l",
            "--link",
            metavar="GIT_URL",
            help="Automatically link and push the new local repo to this remote Git URL",
        )
        parser.add_argument(
            "-m",
            "--message",
            help="Custom commit message to use for the initial repository push",
        )

    def run(self, args):
        print("⌛ Initializing project...\n")
        manifest = capture_project_manifests(args)
        success = LocalInitializer(manifest).run()

        if success and args.link:
            print("\n⌛ Initiating automated repository link shortcut...\n")
            return LinkInitializer(args.link, args.message).run()

        return success
