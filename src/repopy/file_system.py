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

logger = logging.getLogger(__name__)

class FileSystemEngine:

    GITIGNORE_TEMPLATE = '''# Compiled Python files
__pycache__/
*.pyc
 
# Virtual environments
# .venv/
venv/
env/
ENV/

# IDEs and Editors
.vscode/
.idea/
*.swp
*.swo
    
# OS files
.DS_Store
Thumbs_db'''

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


    def create_gitignore(self) -> bool:
        '''Generates a .gitignore file with a basic python gitignore template'''
        gitignore_file = self.project_path / '.gitignore'

        try:
            with open(gitignore_file, 'w') as f:
                f.write(self.GITIGNORE_TEMPLATE)
                return True
            
        except OSError as e:
            logger.error(f'Failed to create gitignore file at {self.project_path}: {e}')
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


    def cleanup(self) -> None:
        '''Removes any partially created project directories if a failure occurs'''
        if self.project_path.exists():
            try:
                shutil.rmtree(self.project_path)
                logger.info(f'Successfully cleaned up half-baked workspace at {self.project_path}')
            except OSError as e:
                logger.error(f'Failed to clean up directory at {self.project_path}: {e}')


    def build_workspace(self) -> bool:
        '''Orchestrate entire file-system creation sequence'''

        if self.create_root_directory():
            if self.initialize_git():
                if self.create_gitignore():
                    if self.create_virtual_environment():
                        return True

        return False