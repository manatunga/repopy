"""
Orchestration Layer. Core supervisor that amalgamates all inspectors and building
tools and manages the entire user request loop from start to finish.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from repopy.engines.file_system import FileSystemEngine
from repopy.engines.git_engine import GitEngine, GitLinkEngine
from repopy.engines.info import WorkspaceInfo
from repopy.templates import format_info_output
from repopy.ui.prompts import (
    confirm_cleanup,
    confirm_cleanup_artifacts,
    confirm_dependency_installation,
)
from repopy.validators.dependencies import has_git, has_python
from repopy.validators.validators import is_valid_git_url, is_valid_project_name

logger = logging.getLogger(__name__)


class LocalInitializer:
    def __init__(self, manifest: dict):
        self.manifest = manifest
        self.project_name = manifest["project_name"]
        self.project_path = Path(self.project_name).resolve()
        self.theme = manifest["theme"]

    def run(self) -> bool:
        """Runs when `repopy local` is called"""
        if not has_python():
            print("⚠️ Python is not installed in the local machine.")
            return False

        if not is_valid_project_name(self.project_name):
            print(f'⚠️ "{self.project_name}" is not a valid directory name.')
            return False

        fs_engine = FileSystemEngine(self.project_path)
        if fs_engine.build_workspace(self.theme, self.manifest):
            print(f"✅ Success! Workspace provisioned inside: {self.project_path}")
            print(f"✅ Layout theme configured: [{self.theme.upper()}]")
            print(fs_engine.get_activation_guide())
            return True

        else:
            print(
                "❌ Construction failed. Triggering cleanup on half-baked directories..."
            )
            fs_engine.cleanup()
            return False


class CloneInitializer:
    def __init__(
        self, repo_url: str, dir_name: str | None, install: bool, no_install: bool
    ):
        self.repo_url = repo_url
        self.dir_name = dir_name if dir_name else None
        self.auto_install = bool(install)
        self.no_install = bool(no_install)

    def run(self) -> bool:
        """Runs when `repopy clone` is called"""
        if not has_python() or not has_git():
            print(
                "❌ Failed to initiate repopy due to absence of Python or Git on local machine."
            )
            return False

        if not is_valid_git_url(self.repo_url):
            print("⚠️ Invalid Git URL format")
            return False

        if self.dir_name:
            predicted_name = self.dir_name
        else:
            cleaned_url = self.repo_url.removesuffix(".git")
            predicted_name = Path(cleaned_url).name

        if not is_valid_project_name(str(predicted_name)):
            print(f'⚠️ "{predicted_name}" is not a valid directory name.')
            return False

        git_engine = GitEngine(self.repo_url, self.dir_name)
        fs_engine = FileSystemEngine(git_engine.project_path)

        if not git_engine.clone_repository():
            return False

        if not fs_engine.create_virtual_environment():
            print(
                f"❌ Failed to create virtual environment at {git_engine.project_path}. Cleaning up half-baked files..."
            )
            fs_engine.cleanup()
            return False

        print("☑️ Cloning complete and .venv has been created.")
        deps = fs_engine.read_requirements()

        if not deps:
            print(
                "No dependencies to install in repository (or requirements.txt is absent)."
            )
            should_install = False

        elif self.no_install:
            print("Skipping installation of dependencies.")
            should_install = False

        elif self.auto_install:
            print("Installing dependencies...")
            should_install = True

        else:
            should_install = confirm_dependency_installation(deps)

        if should_install and not fs_engine.install_dependencies():
            print(f"✅ GitHub repository is ready at {git_engine.project_path}.")
            print(
                f"⚠️ Failed to install dependencies from requirements.txt at {git_engine.project_path}"
            )
            print(fs_engine.get_activation_guide())
            print("To install dependencies, run the following on your terminal:\n")
            print("    pip install -r requirements.txt\n")
            print("Or install them individually by `pip install <module>`\n")

            if confirm_cleanup():
                fs_engine.cleanup()
                print("Half-baked directory has been cleaned up.")
                return False

        print(f"✅ Success! GitHub repository is ready at {git_engine.project_path}.")
        print(fs_engine.get_activation_guide())
        return True


class LinkInitializer:
    def __init__(self, repo_url: str, message: str | None):
        self.repo_url = repo_url
        self.message = (
            message if message else "Initial commit: Workspace structured by repopy"
        )

    def run(self) -> bool:
        """Runs when `repopy link` is called"""
        if not has_git():
            print("⚠️ Git is not installed on this machine.")
            return False

        if not Path(".git").exists():
            print(
                "❌ No local Git repository detected. Please initialize this project first."
            )
            return False

        git_link_engine = GitLinkEngine(self.repo_url, self.message)
        if git_link_engine.link_and_push():
            print(
                f"✅ Success! Your local repository has been linked to {self.repo_url}."
            )
            print(f'Commit message baseline: "{self.message}"')
            return True
        else:
            print(
                f"❌ Failed to establish communication or push to remote repository at {self.repo_url}."
            )
            return False


class CleanInitializer:
    def __init__(self, skip_prompt: bool):
        self.skip_prompt = skip_prompt if skip_prompt else False

    def run(self) -> bool:
        """Runs when `repopy clean` is called"""
        fs_engine = FileSystemEngine(Path.cwd())
        artifacts = fs_engine.find_cleanable_artifacts()

        if not artifacts:
            print("✨ Workspace is already clean, no cleanable artifacts found.")
            return True

        if not self.skip_prompt and not confirm_cleanup_artifacts(artifacts):
            print("✖️ Cleanup cancelled.")
            return False

        success = fs_engine.clean_artifacts(artifacts)
        if success:
            print("✅ Successfully cleaned workspace.")
            return True

        else:
            print("⚠️ Some artifacts could not be removed.")
            return False


class InfoInitializer:
    def __init__(self, as_json: bool, project_root: Path | None = None):
        self.as_json = bool(as_json)
        self.project_root = project_root if project_root else Path.cwd()

    def run(self) -> bool:
        """Runs when `repopy info` is called"""
        info = WorkspaceInfo.from_project_root(self.project_root)

        if self.as_json == True:
            data = {
                "project": {
                    "name": info.project_name,
                    "version": info.project_version,
                    "root": str(info.project_root),
                },
                "runtime": {
                    "python_version": info.python_version,
                },
                "git": {
                    "is_repo": info.is_git_repo,
                    "branch": info.git_branch,
                    "commit": info.latest_commit_hash,
                    "remote_url": info.git_remote,
                },
                "venv": {
                    "is_active": info.is_venv_active,
                    "dependency_count": info.package_count,
                    "dependencies": info.packages,
                },
            }
            print(json.dumps(data, indent=2))

        else:
            print(format_info_output(info))

        return True
