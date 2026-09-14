'''
Orchestration Layer. Core supervisor that amalgamates all inspectors and building
tools and manages the entire user request loop from start to finish.
'''

from pathlib import Path

from repopy.file_system import FileSystemEngine
from repopy.git_engine import GitEngine
from repopy.dependencies import has_python, has_git
from repopy.validators import is_valid_project_name, is_valid_git_url
from repopy.os_detector import is_windows

class LocalInitializer:

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.project_path = Path(project_name)


    def run(self) -> bool:
        '''Runs when `repopy local` is called'''
        if has_python():
            if is_valid_project_name(self.project_name):
                fs_engine = FileSystemEngine(self.project_path)
                if fs_engine.build_workspace():
                    print(f'Success! Your project directory has been created at {self.project_path}.')
                    print('Git has been initialized.\n.gitignore has been generated.')
                    print('To activate your venv, enter the following on the terminal:\n\n')
                    print(f'cd {self.project_path}')
                    if is_windows():
                        print('.\\.venv\\Scripts\\Activate.ps1 (On Powershell)')
                        print('.\\.venv\\Scripts\\activate.bat (On cmd)\n')
                        return True
                    else:
                        print('source .venv/bin/activate')
                        return True

                else:
                    print(f'Failed to create {self.project_path} directory. Cleaning up half-baked files...')
                    fs_engine.cleanup()
                    return False

            else:
                print(f'"{self.project_name}" is not a valid directory name.')
                return False

        else:
            print('Python is not installed in the local machine.')
            return False


class CloneInitializer:

    def __init__(self, repo_url: str, dir_name: str | None):
        self.repo_url = repo_url
        self.dir_name = dir_name if dir_name else None

    def run(self) -> bool:
        '''Runs when `repopy clone` is called'''
        if has_python() and has_git():
            if is_valid_git_url(self.repo_url):
                print('Invalid Git URL format')
                return False
            
            if self.dir_name:
                predicted_name = self.dir_name
            else:
                cleaned_url = self.repo_url.removesuffix('.git')
                predicted_name = Path(cleaned_url).name

            if is_valid_project_name(str(predicted_name)):
                git_engine = GitEngine(self.repo_url, self.dir_name)
                fs_engine = FileSystemEngine(git_engine.project_path)

                if git_engine.clone_repository():
                    if fs_engine.create_virtual_environment():
                        if git_engine.install_dependencies():
                            print(f'Success! GitHub repository has been cloned at {git_engine.project_path}.')
                            print(f'All dependancies have been installed from requirements.txt (if requirements.txt exists)')
                            print('To activate your venv, enter the following on the terminal:\n')
                            print(f'cd {git_engine.project_path}')
                            if is_windows():
                                print('.\\.venv\\Scripts\\Activate.ps1 (On Powershell)')
                                print('.\\.venv\\Scripts\\activate.bat (On cmd)\n')
                                return True
                            else:
                                print('source .venv/bin/activate\n')
                                return True

                        else:
                            print(f'GitHub repository has been clones at {git_engine.project_path}')
                            print(f'Failed to install dependencies from requirements.txt at {git_engine.project_path}')
                            print('To install dependencies, run the following on your terminal:\n')
                            print(f'cd {git_engine.project_path}')
                            print(f'cd {git_engine.project_path}')
                            if is_windows():
                                print('.\\.venv\\Scripts\\Activate.ps1 (On Powershell)')
                                print('.\\.venv\\Scripts\\activate.bat (On cmd)\n')
                            else:
                                print('source .venv/bin/activate\n')
                            print('pip install -r requirements.txt\n')
                            print('Or install them individually by `pip install <module>`')
                            answer = input('If not, would you like to cleanup the new directory? (Y/n): ')

                            if answer.strip().lower() in ['y', 'yes']:
                                git_engine.cleanup()
                                return False
                            else:
                                return True

                    else:
                        print(f'Failed to create {git_engine.project_path} directory. Cleaning up half-baked files...')
                        git_engine.cleanup()
                        return False

                else:
                    return False

            else:
                print(f'"{predicted_name}" is not a valid directory name.')
                return False

        else:
            print(f'Failed to initiate repopy due to absence of Python or Git on local machine.')
            return False    