# Python Binaries

Python binaries package a Python application into an executable form for users who may not manage Python environments directly. They are useful for command-line tools that need simple installation and predictable startup behavior.

## Applied Project

### Project Setup

The applied project is a small image-processing CLI called `Pixelpack Project`. It is built on [Pillow](https://pillow.readthedocs.io/) and [Click](https://click.palletsprojects.com/), with [Nuitka](https://nuitka.net/) for native compilation. This makes it a good fit for Dev Containers because the project depends on a reproducible operating-system-level toolchain, not just isolated Python packages.

### Run the Project

Application, test, lint, container startup, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_pixelpack/README.md).


## Distribution Fundamentals

### Overview

A Python binary distribution packages an application into a **self-contained executable** that includes the application code in compiled or frozen form, third-party dependencies, and any required native libraries. Unlike wheels, a binary distribution does **not require a pre-installed Python environment** on the target machine.

- ✅ Desktop applications
- ✅ CLI tools distributed to non-developers
- ✅ Internal enterprise tools
- ✅ Cross-platform executables

### Python Binary Ecosystem

Python binary packaging is handled by **application freezing or compilation tools**, which convert Python code into native executables.

The most widely used tools are:

| Tool | Type | Description |
|------|------|-------------|
| PyInstaller | Freezer | Bundles Python app into a standalone executable |
| Nuitka | Compiler | Compiles Python code into C/C++ binaries |

Unlike wheel builds, binary tooling is **not standardized around `pyproject.toml`**, though it can still be used for dependency and project metadata.

## PyInstaller vs Nuitka

### PyInstaller

PyInstaller works by analyzing Python imports and bundling the interpreter with dependencies.

It produces:

- Folder-based apps (`dist/app/`)
- Single-file executables (`dist/app.exe` or Linux/macOS binaries)

Characteristics:

- Fast build time
- Simple workflow
- Larger output size
- Runs Python code in a bundled interpreter

### Nuitka

Nuitka compiles Python code into C/C++ and then builds native binaries using a system compiler.

It produces:

- Native executables (`.exe`, ELF, Mach-O)
- Optional standalone distributions

Characteristics:

- Higher runtime performance potential
- Smaller or optimized binaries (depending on project)
- Longer build times
- Requires compiler toolchain (GCC, Clang, or MSVC)

### Project Structure

Binary projects often use a simplified structure:

```text
docslug/
├── src/
│   └── docslug/
│       ├── __main__.py
│       ├── core.py
│       └── cli.py
├── assets/
├── build/
├── dist/
├── pyproject.toml
└── README.md