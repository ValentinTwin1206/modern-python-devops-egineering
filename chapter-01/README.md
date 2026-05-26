# Chapter 1: Python Development Environments

This chapter collects teaching examples about Python runtime and project
environments. The examples focus on where Python is installed, where
packages are written, how command lookup and import lookup differ, and
how environment tools isolate dependencies from the operating system.

## Projects

Each section uses an example project chosen to fit the environment story it teaches. Section 01 uses an admin-style CLI that depends on an APT-only systemd binding, while the other sections use projects that exercise their respective tooling.

### Development

#### Dockerfiles

Each section uses two container images. What changes across the chapter
is where Python lives, where dependencies are installed, and how the
runtime is assembled.

| File | Purpose | Typical contents |
| ---- | ------- | ---------------- |
| `Dockerfile.devEnv` | Development image | An interactive environment that exposes the section's Python model directly: system Python, `venv`, `conda`, or a containerized toolchain. It usually keeps more tools installed, keeps the source tree visible, and is meant for exploration rather than minimal runtime size. |
| `Dockerfile` | Deployment image | A packaging-focused image that builds the application artifact, assembles a cleaner runtime, and starts the final entry point directly. In this chapter that usually means building a wheel first and then installing it into the target runtime, except in the binary section where the final image runs the compiled executable. |

#### Build an Image

Use the chapter-local helper to build either image directly from its
Dockerfile path.

Build only:

```bash
./build.sh build --path section-02/Dockerfile --build-only
```

Build and run:

```bash
./build.sh build --path section-02/Dockerfile.devEnv
```

## Sections

| Folder | Topic | Focus | Details |
| ------ | ----- | ----- | ------- |
| [`section-01/`](./section-01/) | Python system environment | APT-managed Linux Python, system package installs, `PATH`, `sys.path`, `site-packages`, and `dist-packages` | [README](./section-01/README.md) |
| [`section-02/`](./section-02/) | Python `venv` environments | standard-library virtual environments | [README](./section-02/README.md) |
| [`section-03/`](./section-03/) | Python `conda` environments | interpreter and non-Python dependency management | [README](./section-03/README.md) |
| [`section-04/`](./section-04/) | Python dev containers | Ubuntu-based Dev Container with CPython, PyPy, VS Code tooling, lifecycle hooks, port forwarding, and a Nuitka binary container | [README](./section-04/README.md) |
