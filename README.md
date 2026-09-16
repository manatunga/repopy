# repopy

A modular, cross-platform Python CLI workspace manager and developer tooling suite designed to automate reproducible local scaffolding, virtual environment creation, and remote repository synchronization.

![PyPI - Version](https://img.shields.io/pypi/v/repopy?color=orange)&nbsp;&nbsp;&nbsp;
[![CI](https://github.com/manatunga/repopy/actions/workflows/tests.yml/badge.svg)](https://github.com/manatunga/repopy/actions/workflows/tests.yml)&nbsp;&nbsp;&nbsp;
[![Python Versions](https://img.shields.io/pypi/pyversions/repopy.svg)](https://pypi.org)&nbsp;&nbsp;&nbsp;
[![License: MIT](https://img.shields.io/pypi/l/repopy.svg)](https://opensource.org/license/mit)

---

## 🌟 Key Features

- **Lifecycle Project Scaffolding (`repopy init`)**: Replaces manual setup by provisioning clean directory structures, virtual environments, automated `.gitignore` presets, and standardized metadata configurations (`pyproject.toml` or `requirements.txt`).

- **Remote Cloning (`repopy clone`)**: Clones remote Git repositories into structured local footprints and auto-provisions dedicated virtual environments and dependencies.

- **Upstream Linking (`repopy link`)**: Instantly connects an unlinked local workspace to a remote Git upstream, staging files, executing initial commits, and pushing to the default branch in one step.

- **Architectural Themes**: Supports presets (`minimal`, `web_api`, `cli_package`, `data_science`) tailored to the specific packaging needs of the application.

- **Transactional Cleanups**: Employs defensive rollback mechanisms (`shutil.rmtree`) to purge incomplete workspaces if initialization fails midway.

- **Automated Test Suite & CI**: Fully covered by local `pytest` test suites and verified via continuous integration on GitHub Actions.

---

## 🛠️ Architecture & Separation of Concerns

`repopy` is organized into single-responsibility layers:
- **Presentation & Routing (`cli.py`, `prompts.py`, `__main__.py`)**: Evaluates native terminal arguments via `argparse`, orchestrates interactive prompt flows, and handles OS interrupts gracefully.

- **Supervision (`orchestrators.py`)**: Broker layer executing lifecycle validation checks, branch sequencing, and command handoffs.

- **Low-Level Engines (`file_system.py`, `git_engine.py`)**: Decoupled engines handling transactional directory allocations, venv isolation, and direct subprocess execution.

- **Validation & Translation (`validators.py`, `dependencies.py`, `os_detector.py`)**: Sanitizes paths, ensures semantic regex compliance, verifies system binaries (such as `git`), and resolves cross-platform paths.

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
- `data_science`: Notebooks, data folders, and pipeline layouts.
<br>
<br>

### 2. Clone a Remote Project (`repopy clone`)
Fetch a remote repository and immediately auto-provision an isolated `.venv`:

```bash
repopy clone <git-url> -n [custom-project-name]
```

<br>

### 3. Link an Existing Workspace (`repopy link`)
Run inside an existing workspace to push tracking history to an upstream origin:

```bash
repopy link <git-url> -m ["custom-initial-commit-message"]
```

---

## 🧪 Testing & Continuous Integration

Run the test suite using `pytest`:

```bash
pytest -v
```

All contributions and pull requests are validated through our GitHub Actions workflow matrix (`.github/workflows/tests.yml`), running integration and validation tests across supported Python versions.

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
│   ├── test_prompts.py          # Input loop & default manifest tests
│   └── test_validators.py       # Path and schema validation tests
├── pyproject.toml               # PEP 621 packaging configuration
├── LICENSE                      # MIT License
└── README.md
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

---

## Key Review Notes

* Verify the GitHub Actions workflow file path (`.github/workflows/tests.yml`) matches your actual workflow file name so the build badge renders correctly.
* In the `repopy init` theme section, verify that the theme descriptions match what you have mapped out in `templates.py`.