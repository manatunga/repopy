'''
Parser layer. Imports Python's built-in argparse module 
to identify user intent and any extra information passed. 
'''

import argparse

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='repopy: A modular project scaffolder and workflow manager for Python.'
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)

    #---------------------------------------------------------------------------------
    # `repopy init` subcommand
    #---------------------------------------------------------------------------------

    init_parser = subparsers.add_parser(
        'init',
        help='Initializes a standardized Python development workspace in a new directory'
    )

    # Optional argument to add a project_name
    init_parser.add_argument(
        'project_name',
        nargs='?',
        help='Name of the target project folder to create'
    )

    # Project theme shortcut flag (-t / --theme)
    init_parser.add_argument(
        '-t', '--theme',
        choices=['minimal', 'web_api', 'cli_package', 'data_science'],
        help='Pre-select an architectural theme layout'
    )

    # Skip flag (-s / --skip) to bypass input prompts completely
    init_parser.add_argument(
        '-s', '--skip',
        action='store_true',
        help='Skip interactive loops and generate workspace using default values'
    )

    # Link flag (-l / --link) to pass an existing remote URL during creation
    init_parser.add_argument(
        '-l', '--link',
        metavar='GIT_URL',
        help='Automatically link and push the new local repo to this remote Git URL'
    )

    # Custom commit message shortcut allowed directly during init orchestration
    init_parser.add_argument(
        '-m', '--message',
        help='Custom commit message to use for the initial repository push'
    )

    #---------------------------------------------------------------------------------
    # `repopy clone` subcommand
    #---------------------------------------------------------------------------------

    clone_parser = subparsers.add_parser(
        'clone',
        help='Clones a remote Git repository to the local machine'
    )

    # Positional argument to add remote Git URL
    clone_parser.add_argument(
        'repo_url', 
        help='Repository URL from Github to clone locally'
    )

    # Name flag (-n / --name) to pass an optional name for the to-be-cloned repository
    clone_parser.add_argument(
        '-n', '--name',
        help='Name of the project folder'
    )

    # Mutually exclusive commands regarding installing dependencies: 
    # install flag (-i / --install) for installing dependencies, bypassing prompt
    # download-only flag (-d / --download-only) for only fetching dependencies without installing, bypassing prompt
    deps_group = clone_parser.add_mutually_exclusive_group()
    deps_group.add_argument(
        '-i', '--install',
        action='store_true',
        help='Automatically install dependencies without confirmation'
    )

    deps_group.add_argument(
        '-d', '--download-only',
        action='store_true',
        help='Skip dependency installation completely (fetch-only safe mode)'
    )

    #---------------------------------------------------------------------------------
    # `repopy link` subcommand
    #---------------------------------------------------------------------------------

    link_parser = subparsers.add_parser(
        'link',
        help='Stage, commit and link current local repository to a remote Git URL'
    )

    # Positional argument to add a dedicated existing remote Git URL for the local repository
    link_parser.add_argument(
        'repo_url',
        help='Target remote Git repository URL (e.g., git@github.com:user/repo.git)'
    )

    link_parser.add_argument(
        '-m', '--message',
        help='Custom commit message to use instead of the default repopy message'
    )  

    return parser.parse_args()