"""
Templates and layouts manifest layer. Houses raw text templated
and dynamic configuration generators to decouple asset data from
file system logic.
"""

GITIGNORE_TEMPLATE = """# Compiled Python files
__pycache__/
*.pyc
 
# Virtual environments
.venv/
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
Thumbs_db
"""


def generate_pyproject_toml(manifest: dict) -> str:
    """
    Formats a modern PEP 621 compliant configuration string
    dynamically using the provided application manifest attributes
    """

    return f'''[build system]
requires = ["setuptools>=61.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{manifest["project_name"]}"
version = "{manifest["version"]}"
description = "{manifest["description"]}"
authors = [
    {{ name = "{manifest["author"]}" }}
]
requires-python = ">=3.8"
dependencies = []
'''


def generate_readme(manifest: dict) -> str:
    """
    Formats a simple markdown string using provided manifest
    attributes to generate a basic README.md
    """

    return f"""# {manifest["project_name"]}

{manifest.get("description", "A Python project generated with repopy.")}
"""


def format_info_output(info) -> str:
    """
    Formats WorkspaceInfo metadat into a human-readable string
    for CLI display
    """
    lines = []
    lines.append("📊 Repopy Worskpace Information")
    lines.append("=" * 40)

    lines.append(f"📦 Project Name : {info.project_name or 'N/A'}")
    lines.append(f"🔖 Version      : {info.project_version or 'N/A'}")
    lines.append(f"📂 Root Path    : {info.project_root}")
    lines.append(f"🐍 Python       : {info.python_version} or 'N/A")

    lines.append("\n🌿 Git Status")
    if info.is_git_repo:
        lines.append(f"  • Branch     : {info.git_branch or 'N/A'}")
        lines.append(f"  • Commit     : {info.latest_commit_hash or 'N/A'}")
        lines.append(f"  • Remote URL : {info.git_remote or 'None'}")

    else:
        lines.append(f"  • Not a Git repository")

    lines.append("\n⚙️ Virtual Environment")
    if info.is_venv_active:
        lines.append("  • Status     : Active")
    else:
        lines.append("  • Status     : Inactive / Not detected")

    count_str = f"{info.package_count} installed" if info.package_count is not None else "Unknown"
    lines.append(f"  • Packages   : {count_str}")

    return "\n".join(lines)