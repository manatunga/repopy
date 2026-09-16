'''
Prompts layer. Handles interactive terminal questionnaires, input validation
loops, and fallback default configurations.
'''

import re
from pathlib import Path
from repopy.orchestrators import is_valid_project_name

THEME_OPTIONS = {
    '1': 'minimal',
    '2': 'web_api',
    '3': 'cli_package',
    '4': 'data_science'
}


def resolve_unique_project_name() -> str:
    base_name = 'my_python_project'
    target_path = Path(base_name).resolve()

    counter = 1
    while target_path.exists():
        target_path = Path(f'{base_name}_{counter}').resolve()
        counter += 1

    return target_path.name


def capture_project_manifests(cli_args) -> dict:
    version = '1.0.0'
    description = ''
    author = '' 

    if cli_args.project_name:
        project_name = cli_args.project_name

    elif cli_args.skip:
        project_name = resolve_unique_project_name()

    else:
        while True:
            user_input = input('Enter project name: ').strip()

            if not user_input:
                project_name = resolve_unique_project_name()
                break

            if is_valid_project_name(user_input):
                project_name = user_input
                break
            else:
                print('Invalid project name (contains illegal characters or folder exists). Please try again.')

    if cli_args.theme:
        theme = cli_args.theme

    elif cli_args.skip:
        theme = 'minimal'

    else:
        while True:
            print('Available project themes: \n')
            for key, value in THEME_OPTIONS.items():
                print(f'[{key}] {value} ')

            user_input = input('Enter project theme (1-4 OR theme name): ').strip().lower()
            user_choice = user_input if user_input else '1'

            if user_choice.isdigit():
                if user_choice in THEME_OPTIONS:
                    theme = THEME_OPTIONS[user_choice]
                    break
                else:
                    print('Invalid choice, please select between 1-4.')
            else:
                if user_choice in THEME_OPTIONS.values():
                    theme = user_choice
                    break
                else:
                    print('Invalid choice, please try again.')

    if not theme == 'minimal' and not cli_args.skip:
        version_input = input('Enter project version (default: 1.0.0): ').strip()
        while True:
            if re.search(r'[^0-9.]', version_input) and not version_input == '':
                version_input = input('Please enter a valid version number (Only contains numbers and dots/"."): ')
            elif version_input == '':
                break
            else:
                version = version_input
                break

        desc_input = input('Enter description: ')
        description = '' if desc_input.isspace() or not desc_input else desc_input

        author_input = input('Enter author: ')
        author = '' if author_input.isspace() or not author_input else author_input        

    return {
        'project_name': project_name,
        'theme': theme,
        'version': version,
        'description': description,
        'author': author
    }


def confirm_dependency_installation(dependencies: list[str]) -> bool:
    print('\nThis repository contains the following dependencies:')
    for dep in dependencies:
        print(f'    • {dep}')
    
    print()

    try:
        choice = input('Do you want to install these dependencies? [y/N]: ').strip().lower()
        return choice in ('y', 'yes')

    except (KeyboardInterrupt, EOFError):
        print('\nSkipping installation.')
        return False


def confirm_cleanup() -> bool:
    try:
        answer = input('If not, would you like to cleanup the new directory? (Y/n): ').strip().lower()
        return answer in ('y', 'yes')

    except (KeyboardInterrupt, EOFError):
        return False