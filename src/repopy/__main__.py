'''
Main entrypoint of repopy. Brings together the argument parser and
the orchestrators together under a main function.
'''

from repopy.cli import parse_arguments
from repopy.orchestrators import LocalInitializer, CloneInitializer

def main() -> None:
    args = parse_arguments()

    if args.command == 'local':
        print('Working on it...')
        initializer = LocalInitializer(args.project_name)
        initializer.run()

    elif args.command == 'clone':
        print('Working on it...')
        initializer = CloneInitializer(args.repo_url, args.name)
        initializer.run()

    else:
        print('Usage: repopy [local | clone] --help')
        print('Error: Please specify a subcommand')

if __name__ == '__main__':
    main()