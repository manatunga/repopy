'''
Core Engine for the `repopy clone` command. Houses the GitEngine class that
holds the methods required to cone a GitHub repository and install
dependencies.
'''

import shutil
import logging
import subprocess
from pathlib import Path

from repopy.os_detector import is_windows

logger = logging.getLogger(__name__)

class GitEngine:

    def __init__(self, repo_url: str, dir_name: str | None):
        self.repo_url = repo_url

        cleaned_url = repo_url.removesuffix('.git')
        final_name  = dir_name if dir_name else Path(cleaned_url).name

        self.project_path = Path(final_name)


    def clone_repository(self) -> bool:
        '''Clone GitHub repository using the given url to the given directory name'''
        try:
            result = subprocess.run(['git', 'clone', self.repo_url, str(self.project_path)], capture_output=True, text=True)
            return result.returncode == 0
        except OSError as e:
            logger.error(f'Failed to clone repository at {self.project_path}: {e}')
            return False


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

    def cleanup(self) -> None:
        '''Removes any partially created project directories if a failure occurs'''
        if self.project_path.exists():
            try:
                shutil.rmtree(self.project_path)
                logger.info(f'Successfully cleaned up half-baked workspace at {self.project_path}')
            except OSError as e:
                logger.error(f'Failed to clean up directory at {self.project_path}: {e}')
    