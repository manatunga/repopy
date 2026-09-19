"""
Main entrypoint of repopy. Brings together the argument parser and
the orchestrators together under a main function.
"""

import sys

from repopy.cli import parse_arguments
from repopy.orchestrators import CloneInitializer, LinkInitializer, LocalInitializer
from repopy.prompts import capture_project_manifests


def main() -> None:
    try:
        args = parse_arguments()

        if args.command == "init":
            print("⌛ Working on it...\n")
            manifest = capture_project_manifests(args)
            local_initializer = LocalInitializer(manifest)
            success = local_initializer.run()

            if success and args.link:
                print("⌛ Initiating automated repository link shortcut...")
                link_initializer = LinkInitializer(args.link, args.message)
                link_initializer.run()

        elif args.command == "clone":
            print("⌛ Working on it...\n")
            clone_initializer = CloneInitializer(
                args.repo_url, args.name, args.install, args.no_install
            )
            clone_initializer.run()

        elif args.command == "link":
            print("⌛ Working on it...\n")
            link_initializer = LinkInitializer(args.repo_url, args.message)
            link_initializer.run()

        else:
            print("Usage: repopy [init | clone | link] --help")
            print("⚠️ Error: Please specify a subcommand")

    except KeyboardInterrupt:
        print("\n ✖️ Workspace operation cancelled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
