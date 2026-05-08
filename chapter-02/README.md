# Chapter 2: Python Project Configuration

This chapter collects small teaching examples about how Python projects
are configured. The examples in this chapter follow one small package
across six packaging eras, focusing on the files and layouts that
define a project: packaging metadata, dependency declarations, build
configuration, and modern tool-specific project setup.

## Project: Historic Calculator

Historic Calculator is a deliberately small command-line package used to
show how Python project structure changed over time. The application
logic stays simple so each section can focus on packaging choices rather
than feature work.

### Development

#### Dockerfiles

Each section uses two container images. What changes across the chapter
is the packaging workflow, dependency model, and project metadata used
inside the image.

| File | Purpose | Typical contents |
| ---- | ------- | ---------------- |
| `Dockerfile.devEnv` | Development image | An interactive environment that contains the period-appropriate Python interpreter and a copy of the example project. It is meant for trying the packaging steps manually inside the container, following the workflow described in the section README. |
| `Dockerfile` | Deployment image | A packaging-focused image that builds or installs the project according to the era covered in that section and then runs the final command directly. |

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

| Folder | Year | Era | Packaging shape | Details |
| ------ | ---- | --- | --------------- | ------- |
| [`section-01/`](./section-01/) | 2000 | Python 1.6 | `setup.py` with stdlib `distutils` | [README](./section-01/README.md) |
| [`section-02/`](./section-02/) | 2003 | Python 2.3 | `setup.py` with metadata-only dependency hints | [README](./section-02/README.md) |
| [`section-03/`](./section-03/) | 2004 | Python 2.4 | `setup.py` with early `setuptools` | [README](./section-03/README.md) |
| [`section-04/`](./section-04/) | 2010 | Python 2.7 | `setup.py` plus pinned `requirements.txt` | [README](./section-04/README.md) |
| [`section-05/`](./section-05/) | 2016 | Python 3.5 / 2016 workflow | `setup.py` + `setup.cfg` + `requirements*.txt` | [README](./section-05/README.md) |
| [`section-06/`](./section-06/) | 2022 | Python 3.11 / 2022 workflow | `pyproject.toml` only | [README](./section-06/README.md) |
