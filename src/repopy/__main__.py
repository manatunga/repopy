"""
Main entrypoint of repopy. Brings together the argument parser and
the orchestrators together under a main function.
"""

import sys

from repopy.cli import parse_arguments
from repopy.orchestrators import (
    CleanInitializer,
    CloneInitializer,
    LinkInitializer,
    LocalInitializer,
)
from repopy.prompts import capture_project_manifests


def main() -> None:
    try:
        args = parse_arguments()

        if args.command == "init":
            print("⌛ Initializing project...\n")
            manifest = capture_project_manifests(args)
            local_initializer = LocalInitializer(manifest)
            success = local_initializer.run()

            if success and args.link:
                print("\n⌛ Initiating automated repository link shortcut...\n")
                link_initializer = LinkInitializer(args.link, args.message)
                link_success = link_initializer.run()
                sys.exit(0 if link_success else 1)

        elif args.command == "clone":
            print("⌛ Working on it...\n")
            clone_initializer = CloneInitializer(
                args.repo_url, args.name, args.install, args.no_install
            )
            clone_success = clone_initializer.run()
            sys.exit(0 if clone_success else 1)

        elif args.command == "link":
            print("⌛ Working on it...\n")
            link_initializer = LinkInitializer(args.repo_url, args.message)
            link_success = link_initializer.run()
            sys.exit(0 if link_success else 1)

        elif args.command == "clean":
            print("⌛ Scanning for artifacts...\n")
            clean_initializer = CleanInitializer(args.skip_prompt)
            clean_success = clean_initializer.run()
            sys.exit(0 if clean_success else 1)

        else:
            print("Usage: repopy [init | clone | link | clean] --help")
            print("⚠️ Error: Please specify a subcommand")

    except KeyboardInterrupt:
        print("\n ✖️ Workspace operation cancelled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
