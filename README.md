# repopy

A modular, cross-platform Python CLI workspace manager and developer tooling suite designed to automate reproducible local scaffolding, virtual environment creation, and remote repository synchronization.

![PyPI - Version](https://img.shields.io/pypi/v/repopy?color=orange)&nbsp;&nbsp;&nbsp;
[![License: MIT](https://img.shields.io/pypi/l/repopy.svg)](https://opensource.org/license/mit)&nbsp;&nbsp;&nbsp;
[![Python Versions](https://img.shields.io/pypi/pyversions/repopy.svg)](https://pypi.org)

[![CI](https://github.com/manatunga/repopy/actions/workflows/ci.yml/badge.svg)](https://github.com/manatunga/repopy/actions/workflows/ci.yml)&nbsp;&nbsp;&nbsp;
[![codecov](https://codecov.io/github/manatunga/repopy/graph/badge.svg?token=2JRECANC1G)](https://codecov.io/github/manatunga/repopy)&nbsp;&nbsp;&nbsp;
[![type checked - mypy](https://img.shields.io/badge/type--checked-mypy-blue?logo=python)](https://mypy-lang.org)&nbsp;&nbsp;&nbsp;
[![Ruff](https://custom-icon-badges.demolab.com/badge/Ruff-261230.svg?logo=ruff-logo)](#)

---

## 🌟 Key Features

- **Lifecycle Project Scaffolding (`repopy init`)**: Provisions clean directory structures, dedicated virtual environments, automated `.gitignore` and `README.md` templates, and PEP 621 `pyproject.toml` or `requirements.txt` configs.

- **Smart Remote Cloning (`repopy clone`)**: Clones remote Git repositories, creates isolated `.venv` environments, previews declared dependencies, and installs them interactively or via flags.

- **Upstream Linking (`repopy link`)**: Instantly connects an unlinked local workspace to a remote Git upstream, staging files, executing initial commits, and pushing to the default branch in one step.

- **Artifact Pruning (`repopy clean`)**: Recursively scans and purges transient build directories, bytecode caches, and test artifacts (`__pycache__`, `.pytest_cache`, `.coverage`, `build/`, `dist/`, `.ruff_cache`, `.mypy_cache`) with interactive safeguards and automated CI bypasses.

- **Workspace Inspection (`repopy info`)**: Extracts comprehensive project metadata including Python runtime details, project versions, active Git status, and virtual environment dependency counts into formatted terminal cards or machine-readable JSON.

- **Architectural Themes**: Built-in layout presets (`minimal`, `web_api`, `cli_package`, `data_science`) tailored to modern packaging standards.

- **Transactional Safety**: Employs defensive rollback mechanisms (`shutil.rmtree`) to safely purge half-baked directories if setup fails midway, with standardized shell exit codes across all subcommands.

- **Isolated & Tested**: Fully decoupled architecture backed by a 1:1 mapped test suite with 100% branch test coverage.

---

## 🛠️ Architecture & Separation of Concerns

`repopy` is organized into single-responsibility layers:
- **Presentation & Routing (`cli.py`, `prompts.py`, `templates.py`, `__main__.py`)**: Evaluates native terminal arguments via `argparse`, orchestrates interactive prompt flows, and handles OS interrupts gracefully.

- **Supervision (`orchestrators.py`)**: Broker layer executing lifecycle validation checks, branch sequencing, rollback triggers and command handoffs.

- **Low-Level Engines (`file_system.py`, `git_engine.py`, `info.py`)**: Decoupled engines handling transactional directory allocations, venv isolation, dependency installation, subprocess execution, and metadata extraction.

- **Validation & Translation (`validators.py`, `dependencies.py`, `os_detector.py`)**: Sanitizes names and paths, validates Git URLs, verifies host binaries (`python`, `git`), and resolves cross-platform paths.

---

## 📥 Installation

Install the latest release from PyPI:

```bash
pip install repopy
```
Alternatively, you can install the latest development version directly from the source:

```bash
git clone https://github.com/manatunga/repopy.git
cd repopy
pip install -e .
```

---

## 🚀 Usage Guide

### 1. Initialize a Project (`repopy init`)
Generate a new workspace interactively or via CLI flags:

```bash
# Interactive setup
repopy init my-app

# Non-interactive generation with a specific theme (-t/--theme and/or -s/--skip)
repopy init my-api -t web_api -s

# Initialize and immediately connect to a remote repository
repopy init my-cli -t cli_package --link <git-url>
```

#### Available Themes:
- `minimal`: Bare directory setup with `requirements.txt`.
- `web_api`: Layered service layout prepared for modern frameworks.
- `cli_package`: Modular structure configured with PEP 621 compliant `pyproject.toml`.
- `data_science`: Notebooks, data directories (raw, processed), and pipeline layout.

<br>

### 2. Clone a Remote Project (`repopy clone`)
Fetch a remote repository, provision a virtual environment, and manage dependencies:

```bash
# Interactive mode (previews requirements.txt and prompts for installation)
repopy clone <git-url>

# Custom directory name
repopy clone <git-url> -n custom-folder-name

# Auto-install dependencies without prompting (-i/--install)
repopy clone <git-url> -i

# Fetch and provision environment only (skip dependency installation)
repopy clone <git-url> --no-install
```

<br>

### 3. Link an Existing Workspace (`repopy link`)
Run inside an existing workspace to push tracking history to an upstream origin:

```bash
# Link with default initial commit message
repopy link <git-url>

# Link with custom commit message
repopy link <git-url> -m "feat: initial project structure"
```

<br>

### 4. Clean Artifacts (`repopy clean`)
Safely remove build, cache, and test leftovers across the workspace:

```bash
# Interactive mode: scans workspace, previews discovered targets, and prompts for confirmation
repopy clean

# Non-interactive mode: immediately purges all discovered artifacts (ideal for CI/CD pipelines) (-y / --yes)
repopy clean -y
```
#### Cleared Targets:
- Python Bytecode: `__pycache__`, `*.pyc`, `*.pyo`
- Testing & Coverage: `.pytest_cache`, `.coverage`, `htmlcov/`
- Packaging & Builds: `build/`, `dist/`, `*.egg-info`
- Type Checking: `.mypy_cache`, `.ruff_cache`

<br>

### 5. Inspect Workspace Information (`repopy info`)
Display metadata regarding the active project, Git state, and virtual environment:

```bash
# Display formatted human-readable terminal output
repopy info

# Output structured JSON (ideal for programmatic integration and CI scripts) (-j / --json)
repopy info --json
```
### Output Parameters:
- Project Details: Name, version, root path, and Python runtime version.
- Git Status: Active branch, latest commit hash, remote origin URL, and repository status.
- Virtual Environment: Active status, package count, and installed dependencies list.

---

## 🧪 Testing & Continuous Integration

Run the test suite using `pytest`, and style checks with `ruff` and `mypy`:

```bash
# Run unit tests
pytest -v

# Run with full coverage report
pytest --cov=repopy --cov-report=term-missing

# Run linting and format checks
ruff check .
ruff format .

# Run type checks
mypy src/repopy
```

---

## 🗂️ Project Structure

```
repopy/
├── .github/
│   └── workflows/
│       ├── ci.yml               # CI test runner pipeline
│       └── publish.yml          # CD PyPI deployer pipeline
├── src/
│   └── repopy/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Application execution entry
│       ├── cli.py               # CLI subparser configuration
│       ├── commands/            # Command registry & individual command definitions
│       │   ├── __init__.py      # Command registry (COMMANDS dict)
│       │   ├── base.py          # Command(ABC) — shared command contract
│       │   ├── clean.py         # CleanCommand definition
│       │   ├── clone.py         # CloneCommand definition
│       │   ├── info.py          # InfoCommand definition
│       │   ├── init.py          # InitCommand definition
│       │   └── link.py          # LinkCommand definition
│       │
│       ├── dependencies.py      # Binary prerequisite verification
│       ├── file_system.py       # Atomic workspace & venv operations
│       ├── git_engine.py        # Subprocess Git execution engine
│       ├── info.py              # Workspace metadata extraction engine
│       ├── orchestrators.py     # High-level pipeline management
│       ├── os_detector.py       # Cross-platform environment resolver
│       ├── prompts.py           # Dynamic terminal questionnaires
│       ├── templates.py         # Output formatting & asset manifests
│       └── validators.py        # Input sanitation & regex filters
│
├── tests/
│   ├── __init__.py
│   ├── test_cli.py              # CLI argument parser & flag exclusivity tests
│   ├── test_commands.py         # Command registry integrity tests
│   ├── test_dependencies.py     # Binary detection & absence verification tests
│   ├── test_file_system.py      # Workspace scaffolding & requirements parsing tests
│   ├── test_git_engine.py       # Subprocess Git mocking & exit code tests
│   ├── test_info.py             # Workspace metadata extraction tests
│   ├── test_main.py             # CLI dispatching & interrupt lifecycle tests
│   ├── test_orchestrators.py    # Pipeline logic, prompts, and rollback tests
│   ├── test_os_detector.py      # Cross-platform path resolution tests
│   ├── test_prompts.py          # Input loop & default manifest tests
│   ├── test_templates.py        # Output formatting & asset template tests
│   └── test_validators.py       # Path and schema validation tests
│
├── pyproject.toml               # PEP 621 packaging configuration
├── LICENSE                      # MIT License
└── README.md
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
