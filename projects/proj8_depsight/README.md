# Depsight - Real-World Python Project

This section points to Depsight, a real-world Python dependency manager project used as an external case study. The source code lives in the official repository instead of being vendored into this teaching workspace.

## Project Components

The table below lists the main resources that support the Depsight example project.

| Component | Description |
| --------- | ----------- |
| [README.md](README.md) | This local file keeps the teaching repository connected to the external Depsight project. It intentionally stays small because the source code and active project documentation live outside this workspace. |
| [Depsight repository](https://github.com/ValentinTwin1206/depsight-dependency-manager) | The official repository contains the project source, setup instructions, and development workflow. Use that repository as the source of truth when exploring or modifying Depsight. |

## System Requirements

- Git and network access for cloning the official repository.
- The Python version and project tools documented in the official Depsight repository.
- Docker or another isolated development environment if you want to keep the external project separate from this workspace.

## Installation

Clone the official repository outside this teaching project when you want to inspect or run the code:

```bash
git clone https://github.com/ValentinTwin1206/depsight-dependency-manager.git
```

Enter the cloned project directory:

```bash
cd depsight-dependency-manager
```

Follow the setup instructions in that repository's README before running project commands.

## Usage Guide

Navigate to the official [Depsight repository](https://github.com/ValentinTwin1206/depsight-dependency-manager) for the current usage commands and examples. Keeping the commands there avoids duplicating instructions that can drift as the real project changes.

## Development Guide

Make Depsight changes in a clone of the official repository, then use its own tests, linters, and packaging workflow. This local README is only a guidepost from the course material to the external project.