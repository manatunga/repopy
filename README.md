# repopy

A highly modular, cross-platform Python CLI scaffolding tool and library designed to automate the initial configuration of local Python developer workspaces and remote Python repository deployment.

![Static Badge](https://img.shields.io/badge/PyPI_version-0.1.1-orange)&nbsp;&nbsp;&nbsp;
[![Python Versions](https://img.shields.io/pypi/pyversions/repopy.svg)](https://pypi.org)&nbsp;&nbsp;&nbsp;
[![License: MIT](https://img.shields.io/pypi/l/repopy.svg)](https://pypi.org)

---

## 🌟 Key Features

- **Local Scaffolding (`repopy local`)**: Instantly generates standardized directory trees, configures automated multi-line `.gitignore` presets, and initializes clean local Git repositories.

- **Remote Automation (`repopy clone`)**: Downloads remote repositories, parses project structures, and automatically updates localized environment constraints.

- **Isolated Virtual Environments**: Automatically builds localized `.venv` footprints using Python's native compilation layer.

- **Cross-Platform Compatibility**: Automatically detects structural variances between Windows, macOS, and Linux to run direct executions seamlessly.

---

## 🛠️ Architectural Highlights

This package was designed following production-grade software engineering principles:
- **Decoupled Low-Level Engines**: Features standalone layers (`FileSystemEngine` & `GitEngine`) that are entirely decoupled from CLI routing logic, making them fully reusable as an importable library API.

- **Single Responsibility Validation**: Separates terminal argument compilation (`argparse`) from explicit data sanitization filters (`validators.py`) and environmental prerequisite verification (`dependencies.py`).

- **Defensive Error Handling & Auto-Rollback**: Leverages short-circuit evaluations and interactive terminal input cascades. In the event of network or environment breaks during deployment, it offers automated transactional folder cleanups (`shutil.rmtree`) to prevent workspace pollution.

- **Direct-Execution Strategy**: Bypasses unstable, platform-dependent shell environment injections by directly target-executing localized virtual environment binaries (`pip`).

---

## 📥 Installation

You can install `repopy` globally from PyPI using pip:

```bash
pip install repopy
```

Alternatively, you can install the latest development version directly from source:

```bash
git clone https://github.com/manatunga/repopy.git
cd repopy
pip install -e .
```

---

## 🚀 Usage Guide

### 1. Initialize a Local Project from Scratch
Generate a clean, standardized local environment with an operational virtual environment and pre-seeded `.gitignore` file:

```bash
repopy local my-new-app
```

### 2. Clone and Auto-Provision a Remote Codebase
Clone an external codebase, create a virtual environment, scan for a `requirements.txt` file, and automatically install its dependencies:

```bash
repopy clone https://github.comencode/httpx.git -n my-custom-workspace
```

---

## 🗂️ Project Structure

```text
repopy/
├── src/
│   └── repopy/
│       ├── __init__.py         # Package initialization
│       ├── __main__.py         # Application root entry point
│       ├── cli.py              # CLI Argument Parsing layer
│       ├── orchestrators.py    # Architectural workflow supervision
│       ├── os_detector.py      # Cross-platform OS translation utility
│       ├── dependencies.py     # Binary prerequisite verification
│       ├── validators.py       # Data input and path path verification
│       ├── file_system.py      # Low-level file system engine
│       └── git_engine.py       # Low-level shell compilation engine
├── pyproject.toml              # Build-system manifest & CLI script configuration
├── .gitignore
├── LICENSE                     # MIT License
└── README.md                   # Project documentation
```

## 📄 License

Distributed under the MIT License. See `LICENSE` for more details.
