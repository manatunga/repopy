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


class GitLinkEngine:

    def __init__(self, repo_url: str, message: str):
        self.repo_url = repo_url
        self.message = message


    def link_and_push(self) -> bool:
        '''Runs the sequence of Git terminal execution blocks to link the repo'''
        try:
            stage_result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
            if stage_result.returncode != 0:
                return False

            commit_result = subprocess.run(['git', 'commit', '-m', self.message], capture_output=True, text=True)
            if commit_result.returncode != 0:
                if 'nothing to commit' not in commit_result.stdout:
                    return False

            branch_result = subprocess.run(['git', 'branch', '-M', 'main'], capture_output=True, text=True)
            if branch_result.returncode != 0:
                return False

            remote_result = subprocess.run(['git', 'remote', 'add', 'origin', self.repo_url], capture_output=True, text=True)
            if remote_result.returncode != 0:
                return False

            push_result = subprocess.run(['git', 'push', '-u', 'origin', 'main'], text=True)
            if push_result.returncode != 0:
                return False

            return True

        except OSError as e:
            logger.error(f'Failed to execute Git linking operationsL {e}')
            return False
        