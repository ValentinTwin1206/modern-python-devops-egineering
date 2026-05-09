# Python `Conda` environments

This page covers Conda, both as a package manager and as an environment manager. Conda can replace the usual `pip` plus `venv` workflow when you need one tool to manage Python, Python packages, and non-Python packages together.

## Tiny Webserver Project

The example uses the tiny Bottle web server project. Step-by-step development workflow instructions live in the section README at [`README.md`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-03/README.md).

### Used DevTools

These tools cover the example application's runtime package, development utilities, and the Conda workflow discussed in this section.

| Component            | Description |
| -------------------- | ----------- |
| [Bottle](https://bottlepy.org/docs/dev/) | Bottle is the runtime dependency for the tiny web server example. It gives the Conda environment a real Python package to manage alongside the interpreter itself. |
| [Karva](https://matthewmckee4.github.io/karva/) | Karva is the test runner used in the chapter's development workflow. Here it also demonstrates that Conda environments can include Python tools installed through `pip` when needed. |
| [Ruff](https://docs.astral.sh/ruff/) | Ruff is the linter and formatter used for code-quality checks. It helps show that a Conda-managed environment can bundle both application and tooling dependencies in one place. |
| [Conda](https://docs.conda.io/) | Conda is the environment manager and package manager discussed in this section. It is important here because it can manage Python itself as well as non-Python dependencies. |

### Project Files

These project files show how the Conda environment is declared and how the example is built in both development and deployment images.

| Component            | Description |
| -------------------- | ----------- |
| [`environment.yml`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-03/environment.yml) | This file declares the Conda environment for the example project. It pins the interpreter and Conda packages, and it also documents the extra tools installed through `pip`. |
| [`Dockerfile.devEnv`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-03/Dockerfile.devEnv) | This development image installs Miniconda and creates the named environment from `environment.yml`. It provides a reproducible Conda setup that matches the layout described in the section. |
| [`Dockerfile`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-03/Dockerfile) | This deployment image builds the project wheel and runs it inside a dedicated Conda environment. It shows how the same environment model can be used beyond local inspection. |
| [`pyproject.toml`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-03/pyproject.toml) | This file defines the Python package metadata for the tiny web server. It is the source of the package that later gets installed into the Conda environment. |

## Install `Conda`

On Debian-based Linux, a common starting point is Miniconda. It provides the minimal pieces needed to run `conda` without installing the full Anaconda distribution. User installs typically live under `~/miniconda3`, while this section's Docker image installs Miniconda under `/opt/conda`.

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

## `Conda` environment model

Conda differs from `venv` because it can manage the Python interpreter version itself and install non-Python dependencies from Conda channels. `pip` installs Python packages into an existing environment; `conda` installs packages of many kinds into Conda environments. That makes it a common choice for scientific work where Python packages depend on native libraries such as BLAS, CUDA, or GDAL.

### Environment location on Debian-based Linux

On Debian-based Linux, a Conda environment lives under the Conda installation prefix rather than inside the project directory. For user installs, that prefix is often `~/miniconda3` or `~/anaconda3`. In this section's Docker setup, Miniconda is installed under `/opt/conda`, so the named environment lives at `/opt/conda/envs/tiny-webserver`.

Because Conda environments are usually stored centrally, environment names need to be unique within one Conda installation. Use descriptive names such as `tiny-webserver` instead of generic names such as `venv`, especially when you work on multiple projects on the same machine.

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

Conda does not download packages from `pypi.org` by default. In its default configuration, it installs packages from Anaconda-hosted Conda channels such as `repo.anaconda.com`, and many projects use community channels such as `conda-forge` for broader package availability.

Those Conda channels are package repositories, but they are not mirrors of the Python Package Index at `pypi.org`. Some packages are available from Conda channels and not from PyPI, especially compiled or data-science-oriented packages. Other Python packages are available on PyPI but not from the Conda channels you use, which is why Conda environments often include `pip` as a fallback.

| Source type            | Typical tool      | Best fit                                                       |
| ---------------------- | ----------------- | -------------------------------------------------------------- |
| Conda channel package  | `conda install`   | Python itself, native libraries, and packages published to Conda channels |
| PyPI package           | `pip install`     | Packages downloaded from `pypi.org` when Conda channels do not provide them |

Using both tools in one environment is normal in Conda workflows, but it helps to install Conda packages first and use `pip` only for packages that Conda does not provide. That keeps Conda's package records in `conda-meta/` as complete as possible before PyPI packages are layered on top.

## Workflow

### Create and activate

Create a fresh environment with Python and `pip`:

```bash
conda create -y -n fresh-env python=3.12 pip
```

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

Deactivate the environment when you are done working in it:

```bash
conda deactivate
```

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
- ✅ Fits teams that already use Anaconda or Conda-based tooling across platforms and languages.

### Cons

- ⚠️ Heavier than `venv` in both tooling footprint and environment size.
- ⚠️ Maintains a separate ecosystem alongside PyPI, which means you often need to understand both `conda` and `pip`.
- ⚠️ Dependency solving can be slower than simpler PyPI-only workflows.
- ⚠️ Pure-Python projects with straightforward PyPI dependencies are often simpler with `venv` and `pip` or `uv`.
