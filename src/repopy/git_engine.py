'''
Core Engine for the `repopy clone` command. Houses the GitEngine class that
holds the methods required to cone a GitHub repository and install
dependencies.
'''

import shutil
import logging
import subprocess
from pathlib import Path

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
        