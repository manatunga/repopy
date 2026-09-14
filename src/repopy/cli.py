'''
Parser layer. Imports Python's built-in argparse module 
to identify user intent and any extra information passed. 
'''

import argparse

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', required=True)

    local_parser = subparsers.add_parser('local')
    local_parser.add_argument('project_name', help='Name of the project folder')

    clone_parser = subparsers.add_parser('clone')
    clone_parser.add_argument('repo_url', help='Repository URL from Github to clone')
    clone_parser.add_argument('-n', '--name', action='store', help='Name of the project folder')

    return parser.parse_args()