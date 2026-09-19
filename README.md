# repopy

A modular, cross-platform Python CLI workspace manager and developer tooling suite designed to automate reproducible local scaffolding, virtual environment creation, and remote repository synchronization.

![PyPI - Version](https://img.shields.io/pypi/v/repopy?color=orange)&nbsp;&nbsp;&nbsp;
[![License: MIT](https://img.shields.io/pypi/l/repopy.svg)](https://opensource.org/license/mit)&nbsp;&nbsp;&nbsp;
[![Python Versions](https://img.shields.io/pypi/pyversions/repopy.svg)](https://pypi.org)

[![CI](https://github.com/manatunga/repopy/actions/workflows/tests.yml/badge.svg)](https://github.com/manatunga/repopy/actions/workflows/tests.yml)&nbsp;&nbsp;&nbsp;
[![codecov](https://codecov.io/github/manatunga/repopy/graph/badge.svg?token=2JRECANC1G)](https://codecov.io/github/manatunga/repopy)&nbsp;&nbsp;&nbsp;
[![type checked - mypy](https://img.shields.io/badge/type--checked-mypy-blue?logo=python)](https://mypy-lang.org)&nbsp;&nbsp;&nbsp;
[![Ruff](https://custom-icon-badges.demolab.com/badge/Ruff-261230.svg?logo=ruff-logo)](#)

---

## 🌟 Key Features

- **Lifecycle Project Scaffolding (`repopy init`)**: Provisions clean directory structures, dedicated virtual environments, automated `.gitignore` templates, and PEP 621 `pyproject.toml` or `requirements.txt` configs.

- **Smart Remote Cloning (`repopy clone`)**: Clones remote Git repositories, creates isolated `.venv` environments, previews declared dependencies, and installs them interactively or via flags.

- **Upstream Linking (`repopy link`)**: Instantly connects an unlinked local workspace to a remote Git upstream, staging files, executing initial commits, and pushing to the default branch in one step.

- **Architectural Themes**: Built-in layout presets (`minimal`, `web_api`, `cli_package`, `data_science`) tailored to modern packaging standards.

- **Transactional Cleanups**: Employs defensive rollback mechanisms (`shutil.rmtree`) to safely purge half-baked directories if setup fails midway.

- **Isolated & Tested**: Fully decoupled architecture backed by comprehensive unit and mock test suites.

---

## 🛠️ Architecture & Separation of Concerns

`repopy` is organized into single-responsibility layers:
- **Presentation & Routing (`cli.py`, `prompts.py`, `__main__.py`)**: Evaluates native terminal arguments via `argparse`, orchestrates interactive prompt flows, and handles OS interrupts gracefully.

- **Supervision (`orchestrators.py`)**: Broker layer executing lifecycle validation checks, branch sequencing, rollback triggers and command handoffs.

- **Low-Level Engines (`file_system.py`, `git_engine.py`)**: Decoupled engines handling transactional directory allocations, venv isolation, dependency installation and direct subprocess execution.

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

# Non-interactive generation with a specific theme
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

# Auto-install dependencies without prompting
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

---

## 🧪 Testing & Continuous Integration

Run the test suite using `pytest`:

```bash
pytest -v
```

---

## 🗂️ Project Structure

```
repopy/
├── .github/
│   └── workflows/
│       └── tests.yml            # CI test runner pipeline
├── src/
│   └── repopy/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Application execution entry
│       ├── cli.py               # CLI subparser configuration
│       ├── dependencies.py      # Binary prerequisite verification
│       ├── file_system.py       # Atomic workspace & venv operations
│       ├── git_engine.py        # Subprocess Git execution engine
│       ├── orchestrators.py     # High-level pipeline management
│       ├── os_detector.py       # Cross-platform environment resolver
│       ├── prompts.py           # Dynamic terminal questionnaires
│       ├── templates.py         # Static asset definitions & manifests
│       └── validators.py        # Input sanitation & regex filters
├── tests/
|   ├── __init__.py
│   ├── test_cli.py              # CLI argument parser & flag exclusivity tests
│   ├── test_dependencies.py     # Binary detection & absence verification tests
│   ├── test_file_system.py      # Workspace scaffolding & requirements parsing tests
│   ├── test_git_engine.py       # Subprocess Git mocking & exit code tests
│   ├── test_main.py             # CLI dispatching & interrupt lifecycle tests
│   ├── test_orchestrators.py    # Pipeline logic, prompts, and rollback tests
│   ├── test_os_detector.py      # Cross-platform path resolution tests
│   ├── test_prompts.py          # Input loop & default manifest tests
│   ├── test_templates.py        # PEP 621 generator & asset template tests
│   └── test_validators.py       # Path and schema validation tests
├── pyproject.toml               # PEP 621 packaging configuration
├── LICENSE                      # MIT License
└── README.md
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
