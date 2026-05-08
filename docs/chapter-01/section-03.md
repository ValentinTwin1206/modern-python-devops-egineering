# Python `conda` environments

This page covers Conda, both as a package manager and as an environment manager. The example uses the tiny Bottle web serverproject. Step-by-step development workflow instructions live in the section README at [`README.md`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-03/README.md).

| Component            | Description                                      | Role in this section                                  |
| -------------------- | ------------------------------------------------ | ----------------------------------------------------- |
| [Bottle](https://bottlepy.org/docs/dev/) | Lightweight Python web framework.              | Example application dependency and web server         |
| [Karva](https://matthewmckee4.github.io/karva/) | Python test runner written in Rust.            | Test runner used for the section test workflow        |
| [Ruff](https://docs.astral.sh/ruff/) | Fast Python linter and formatter.              | Linter used for the section code-quality checks       |
| [Conda](https://docs.conda.io/) | Cross-language package and environment manager. | Environment boundary and package source manager for this section |

!!! info "`Dockerfile.devEnv` and `Dockerfile`"
    The development image installs Miniconda, creates an environment named `tiny-webserver` from `environment.yml`, and exposes the project source through `PYTHONPATH` rather than installing it. The deployment image builds a wheel, creates a dedicated Conda environment, installs the wheel with `pip`, and starts the `tiny-webserver` entry point.

## Install Conda

On Debian-based Linux, a common starting point is Miniconda. User installs typically live under `~/miniconda3`, while this section's Docker image installs Miniconda under `/opt/conda`.

Download the Miniconda installer:

```bash
curl -LsSf -o miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

Run the installer into a user-local prefix:

```bash
bash miniconda.sh -b -p "$HOME/miniconda3"
```

Put Conda on `PATH` for the current shell:

```bash
export PATH="$HOME/miniconda3/bin:$PATH"
```

Initialize Conda for future Bash shells:

```bash
conda init bash
```

Create a fresh environment with Python and `pip`:

```bash
conda create -y -n fresh-env python=3.12 pip
```

## Conda environment model

Conda differs from `venv` because it can manage the Python interpreter version itself and install non-Python dependencies from Conda channels. That makes it a common choice for scientific work where packages depend on native libraries such as BLAS, CUDA, or GDAL.

### Environment location on Debian-based Linux

On Debian-based Linux, a Conda environment lives under the Conda installation prefix rather than inside the project directory. For user installs, that prefix is often `~/miniconda3` or `~/anaconda3`. In this section's Docker setup, Miniconda is installed under `/opt/conda`, so the named environment lives at `/opt/conda/envs/tiny-webserver`.

### Environment layout

In the official Miniconda image, a fresh Conda environment created with `conda create -n fresh-env python=3.12 pip` looks like this:

```text
<conda-prefix>/
├── bin/
│   └── conda
├── envs/
│   └── fresh-env/
│       ├── bin/
│       │   ├── pip
│       │   ├── pip3
│       │   ├── python
│       │   ├── python3
│       │   └── python3.12
│       ├── compiler_compat/
│       ├── conda-meta/
│       ├── etc/
│       ├── include/
│       │   └── python3.12/
│       ├── lib/
│       │   └── python3.12/
│       │       └── site-packages/
│       │           ├── packaging/
│       │           ├── pip/
│       │           ├── setuptools/
│       │           └── wheel/
│       ├── man/
│       ├── share/
│       ├── ssl/
│       └── x86_64-conda-linux-gnu/
└── pkgs/
```

In this section's Docker setup, the same layout lives under `/opt/conda/envs/tiny-webserver`, and additional project packages such as Bottle, Ruff, and Karva are added on top of that fresh baseline.

### Key directories and files

- **`/opt/conda/bin/conda`:** is the top-level Conda executable that manages environments and packages.

- **`<conda-prefix>/envs/<name>/`:** is the named environment directory; in this section's development image that path is `/opt/conda/envs/tiny-webserver`.

- **`bin/`:** contains the environment-local executables, including Python, `pip`, and any console scripts installed into the environment.

- **`lib/python3.12/site-packages/`:** contains the Python packages installed into the Conda environment, regardless of whether they came from Conda channels or from `pip`.

- **`conda-meta/`:** stores Conda's package records and history for the environment.

- **`compiler_compat/`:** contains linker and compiler-compatibility helpers bundled into the environment.

- **`pkgs/`:** stores the shared package cache for the Conda installation prefix.

### Activation and import path

- **Environment-local interpreter:** after `conda activate tiny-webserver`, the environment's `python3` becomes the first interpreter on `PATH`.

- **Environment-local packages:** imports resolve from `/opt/conda/envs/tiny-webserver/lib/python3.12/site-packages/` in this section's Docker image.

- **Environment location:** unlike `venv`, the environment does not live inside the project folder by default; it lives under the Conda installation prefix.

  ```python
  import sys
  print(sys.prefix)
  print(sys.executable)
  ```

### Environment definition

The environment is described in `environment.yml`:

```yaml
name: tiny-webserver
channels:
  - conda-forge
dependencies:
  - python=3.12
  - bottle=0.13.4
  - ruff=0.15.12
  - pip
  - pip:
      - karva>=0.0.1a5
```

Most packages come from `conda-forge`. Karva is installed through `pip` because it is published on PyPI.

### Package sources

| Source type            | Typical tool      | Best fit                                                       |
| ---------------------- | ----------------- | -------------------------------------------------------------- |
| Conda channel package  | `conda install`   | Python itself, native libraries, and packages published to Conda channels |
| PyPI package           | `pip install`     | Packages that are only published to PyPI                       |

Using both tools in one environment is normal in Conda workflows, but it helps to install Conda packages first and use `pip` only for packages that Conda does not provide.

## Workflow

### Create and activate

Create the environment from the section folder:

```bash
conda env create -f environment.yml
```

Activate the environment:

```bash
conda activate tiny-webserver
```

### Add packages

=== "Conda channel"

    Add a package from a Conda channel:

    ```bash
    conda install -c conda-forge <package>
    ```

=== "PyPI package"

    Add a package from PyPI when it is not available from your chosen Conda channels:

    ```bash
    python -m pip install <package>
    ```

Snapshot the environment requirements back to YAML:

```bash
conda env export --from-history > environment.yml
```

### Run the project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-03/README.md).

## Inspection

Show the active environment name:

```bash
echo $CONDA_DEFAULT_ENV
```

List all Conda environments:

```bash
conda env list
```

Show the active interpreter inside the Conda environment:

```bash
python3 -c "import sys; print(sys.prefix); print(sys.executable)"
```

## Tradeoffs

### Pros

- ✅ Manages Python interpreter versions as part of the environment definition.
- ✅ Installs non-Python packages from Conda channels alongside Python packages.
- ✅ Works well for scientific or compiled dependencies that are awkward in plain `pip` workflows.

### Cons

- ⚠️ Heavier than `venv` in both tooling footprint and environment size.
- ⚠️ Maintains a separate ecosystem alongside PyPI, which means you often need to understand both `conda` and `pip`.
- ⚠️ Dependency solving can be slower than simpler PyPI-only workflows.
