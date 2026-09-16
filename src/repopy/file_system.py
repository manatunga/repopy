'''
Core Engine for the `repopy local` command. Houses the FileSystemEngine class
that holds the methods required to manipulate directories, create virtural
environments and create .gitignore and README.md templates.
'''

import venv
import shutil
import logging
import subprocess
from pathlib import Path

from repopy.os_detector import is_windows
from repopy.templates import GITIGNORE_TEMPLATE, generate_pyproject_toml

logger = logging.getLogger(__name__)

class FileSystemEngine:

    def __init__(self, project_path: Path):
        self.project_path = project_path


    def create_root_directory(self) -> bool:
        '''Creates new project directory with user-specified project name'''
        try:
            self.project_path.mkdir(parents=True, exist_ok=True)
            return True
        
        except OSError as e:
            logger.error(f'Failed to create directory at {self.project_path}: {e}')
            return False


    def create_theme_directories(self, theme: str, project_name: str):
        '''Maps and structures the child directory tree based on the project theme'''
        if theme == 'web_api':
            sub_dirs = ['src/app', 'src/app/routes', 'src/app/models']

        elif theme == 'cli_package':
            sub_dirs = [f'src/{project_name}', 'tests']

        elif theme == 'data_science':
            sub_dirs = ['data/raw', 'data/processed', 'notebooks', 'src/pipeline']

        else:
            return True

        try:
            for folder in sub_dirs:
                target_folder_path = (self.project_path / folder).resolve()
                target_folder_path.mkdir(parents=True, exist_ok=True)

            return True

        except OSError as e:
            logger.error(f'Failed to build nested structures for theme {theme}: {e}')
            return False


    def write_theme_configurations(self, theme: str, manifest: dict) -> bool:
        '''Deploys standard configuration templates (gitignore, requirements.txt or toml)'''
        try:
            gitignore_path = self.project_path / '.gitignore'
            with open(gitignore_path, 'w') as f:
                f.write(GITIGNORE_TEMPLATE)

            if theme == 'minimal':
                req_path = self.project_path / 'requirements.txt'
                with open(req_path, 'w') as f:
                    f.write('')

            else:
                toml_content = generate_pyproject_toml(manifest)
                toml_path = self.project_path / 'pyproject.toml'
                with open(toml_path, 'w') as f:
                    f.write(toml_content)

            return True

        except OSError as e:
            logger.error(f'Failed to deploy structural file sheets: {e}')
            return False


    def create_virtual_environment(self) -> bool:
        '''Initializes a python virtual environment'''
        venv_dir = self.project_path / '.venv'

        try:
            venv.create(venv_dir, with_pip=True)
            return True

        except Exception as e:
            logger.exception(f'Failed to create virtual environment at {self.project_path}: {e}')
            return False


    def initialize_git(self) -> bool:
        '''Initializes git within the newly created project directory'''
        try:
            result = subprocess.run(['git', 'init'], cwd=self.project_path, capture_output=True, text=True)
            return result.returncode == 0
        except OSError as e:
            logger.error(f'Unable to initialize git at {self.project_path}: {e}')
            return False


    def read_requirements(self) -> list[str]:
        '''Read repository dependencies if requirements.txt exists and displays them'''
        req_path = self.project_path / 'requirements.txt'
        if not req_path.is_file():
            return []
        
        with open(req_path, 'r') as f:
            lines = [
                cleaned_line
                for line in f
                if (cleaned_line := line.strip()) and not cleaned_line.startswith('#')
            ]

        return lines
    

    def install_dependencies(self) -> bool:
        '''Install repository dependencies if requirements.txt is present'''
        req_file = self.project_path / 'requirements.txt'

        if not req_file.exists():
            return True

        if is_windows():
            pip_path = self.project_path / '.venv' / 'Scripts' / 'pip.exe'
        else:
            pip_path = self.project_path / '.venv' / 'bin' / 'pip'

        try:
            result = subprocess.run([str(pip_path), 'install', '-r', str(req_file)], capture_output=True, text=True)
            return result.returncode == 0
        
        except OSError as e:
            logger.error(f'Failed to install dependencies at {self.project_path}: {e}')
            return False


    def get_activation_guide(self) -> str:
        if is_windows():
            venv_activation = '''
    .\\.venv\\Scripts\\Activate.ps1 (if on Powershell)
    .\\.venv\\Scripts\\activate.bat (if on cmd)\n
'''
        else:
            venv_activation = '''
    source .venv/bin/activate\n
'''
        
        return f'''
To activate the virtual environment and get started, enter the following:

    cd {self.project_path}

{venv_activation}
'''


    def cleanup(self) -> None:
        '''Removes any partially created project directories if a failure occurs'''
        if self.project_path.exists():
            try:
                shutil.rmtree(self.project_path)
                logger.info(f'Successfully cleaned up half-baked workspace at {self.project_path}')
            except OSError as e:
                logger.error(f'Failed to clean up directory at {self.project_path}: {e}')


    def build_workspace(self, theme: str, manifest: dict) -> bool:
        '''Orchestrate entire file-system creation sequence'''

        if self.create_root_directory():
            if self.initialize_git():
                if self.create_theme_directories(theme, manifest['project_name']):
                    if self.write_theme_configurations(theme, manifest):
                        if self.create_virtual_environment():
                            return True

        return False