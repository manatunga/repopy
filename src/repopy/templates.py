'''
Templates and layouts manifest layer. Houses raw text templated 
and dynamic configuration generators to decouple asset data from 
file system logic.
'''

GITIGNORE_TEMPLATE = '''# Compiled Python files
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
'''

def generate_pyproject_toml(manifest: dict) -> str:
    '''
    Formats a modern PEP 621 compliant configuration string 
    dynamically using the provided application manifest attributes
    '''

    return f'''[build system]
requires = ["setuptools>=61.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{manifest['project_name']}"
version = "{manifest['version']}"
description = "{manifest['description']}"
authors = [
    {{ name = "{manifest['author']}" }}
]
requires-python = ">=3.8"
dependencies = []
'''

def generate_readme(manifest: dict) -> str:
    '''
    Formats a simple markdown string using provided manifest 
    attributes to generate a basic README.md
    '''

    return f'''# {manifest['project_name']}

{manifest.get('description', 'A Python project generated with repopy.')}
'''