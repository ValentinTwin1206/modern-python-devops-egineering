---
description: "Create a MkDocs documentation site from repository README files and slim section READMEs."
name: "Create MkDocs Docs"
argument-hint: "Optional: specify MkDocs theme or extra documentation constraints"
agent: "agent"
---

You are working in the `modern-python-engineering` repository. Create a clear MkDocs-based technical documentation site for junior developers, using the existing repository README files as the source material.

Additional user constraints, if any:

```text
${input:constraints:No additional constraints.}
```

## Goals

1. Create a MkDocs documentation site under `docs/`.
2. Add a root-level `mkdocs.yml` configuration.
3. Use information from the existing README files as the source of truth.
4. Keep the documentation clear, direct, concise, and understandable for junior developers.
5. Slim down the section README files only. Do not replace chapter README files with tiny stubs unless required for link correctness.

## Required Navigation

Configure `mkdocs.yml` with exactly two top-level navigation entries:

- `Chapter 01`
- `Chapter 02`

Each chapter must expand into section pages in the left navigation:

```yaml
nav:
  - Chapter 01:
      - Section 01: chapter-01/section-01.md
      - Section 02: chapter-01/section-02.md
      - Section 03: chapter-01/section-03.md
      - Section 04: chapter-01/section-04.md
      - Section 05: chapter-01/section-05.md
  - Chapter 02:
      - Section 01: chapter-02/section-01.md
      - Section 02: chapter-02/section-02.md
      - Section 03: chapter-02/section-03.md
      - Section 04: chapter-02/section-04.md
      - Section 05: chapter-02/section-05.md
      - Section 06: chapter-02/section-06.md
```

If the repository sections differ from this list, inspect the filesystem and adapt the section list to the actual chapter folders while preserving the top-level names `Chapter 01` and `Chapter 02`.

## Expected Files

Create this documentation structure:

```text
mkdocs.yml
docs/
  chapter-01/
    section-01.md
    section-02.md
    section-03.md
    section-04.md
    section-05.md
  chapter-02/
    section-01.md
    section-02.md
    section-03.md
    section-04.md
    section-05.md
    section-06.md
```

Do not store generated MkDocs pages outside `docs/`.

## Content Rules For MkDocs Pages

For each generated page:

- Start with a plain, descriptive H1 title.
- Explain the section purpose in one or two short paragraphs.
- Include the important commands from the original README where useful.
- Explain what each command does in direct language.
- Prefer short sections and code blocks over long prose.
- Preserve technically important details from the original README files.
- Remove duplicated content when a concept is already explained clearly elsewhere.
- Use relative links that work in MkDocs.
- Avoid marketing language, filler, and vague claims.
- Write for junior developers who know basic Python and the shell but may not know packaging history, Docker, Conda, Pipenv, Dev Containers, or Nuitka yet.
- Add background information when it improves understanding of a tool, workflow, or historical choice.
- Prefer tables when comparing technologies, file roles, command choices, or packaging eras.
- Prefer tabs when showing equivalent workflows, such as Docker versus host usage, only if the chosen MkDocs setup supports tabbed content.
- Avoid punctuation-heavy prose. Do not overuse colons or dashes in explanatory text.
- Follow The Chicago Manual of Style for prose, headings, capitalization, punctuation, and sentence structure.
- Use sentence-style capitalization for headings unless an existing project title, tool name, or proper noun requires otherwise.
- Keep wording concise and instructional. Prefer active voice and direct verbs.
- Use serial commas in prose.
- Treat command names, file names, package names, and tool names as technical terms. Format them with inline code when referring to literal values.

## Command And Code Block Style

Apply these rules to both generated MkDocs pages and rewritten section README files:

- Put a short explanation sentence before every command code block.
- Prefer one focused code block per command.
- Do not merge unrelated commands into one large code block.
- Group multiple commands in one code block only when they must be run together as one workflow.
- Keep code blocks clean: no shell prompts, no inline comments, and no expected output mixed with commands.
- If expected output is important, put it in a separate `text` code block after a short explanation sentence.
- Use the correct fence language, such as `bash`, `toml`, `yaml`, `json`, `python`, or `text`.
- Explain commands in plain language before the block instead of adding comments inside the block.

## Section README Shrink Rules

Update only the README files inside concrete section folders, for example:

- `chapter-01/section-01/README.md`
- `chapter-01/section-02/README.md`
- `chapter-02/section-06/README.md`

Do not apply this shrink rule to:

- root `README.md`
- `chapter-01/README.md`
- `chapter-02/README.md`

Each section README should become a normal, short project README with this structure:

```markdown
# <Section Title>

One short paragraph explaining what this section demonstrates.

## Required Developer Tools

Short list of tools needed to work with this section.

### With Docker

Steps to build, run, or inspect the section through the chapter helper and container files.

### On Host

Steps to install and set up the tools needed to work directly on the host system.

## Usage Guide

Commands needed to build, run, or inspect the example.

## Development Guide

Commands needed for local development, checks, formatting, tests, builds, or packaging.
```

The `Required Developer Tools` section must be specific to the section. Include only tools that are actually needed, such as Python, Docker or Podman, `uv`, `pip`, `setuptools`, `build`, `pipenv`, `conda`, Node.js, npm, the Dev Containers CLI, or compiler toolchains. Do not list tools that the section does not use.

Under `With Docker`, explain the container-based path first. Use the chapter helper where it applies.

Under `On Host`, explain the direct host setup. Include installation or setup commands for the section's tools when those commands are reliable and appropriate for the represented era.

For Chapter 02, keep `On Host` historically appropriate. Older sections should use the setup style and commands a maintainer of that year would reasonably use.

Use only commands that are actually relevant for that section. Prefer this style:

Install the project dependencies with `uv`:

```bash
uv sync
```

Run the tiny web server:

```bash
uv run tiny-webserver
```

Run the tests:

```bash
uv run karva test tests/
```

Run the linter:

```bash
uv run ruff check .
```

Build the wheel:

```bash
uv build --wheel
```

Install Pipenv dependencies for development:

```bash
pipenv install --dev
```

Run the application through Pipenv:

```bash
pipenv run tiny-webserver
```

Create the conda environment:

```bash
conda env create -f environment.yml
```

Build a Python package with the standard build frontend:

```bash
python -m build
```

Build legacy source and wheel distributions:

```bash
python setup.py sdist bdist_wheel
```

Build a section container image through the chapter helper:

```bash
../build.sh build --path section-01/Dockerfile --build-only
```

Do not invent commands that the project cannot run. Inspect `pyproject.toml`, `setup.py`, `requirements*.txt`, `Pipfile`, `environment.yml`, Dockerfiles, and existing README content before choosing commands.

## Chapter 02 README Perspective

When rewriting README files under `chapter-02/section-*`, write from the perspective of a project maintainer working in the historical year represented by that section.

Use the year and packaging era from `chapter-02/README.md` as the source of truth. For example:

- `chapter-02/section-01` represents the year 2000, so its README should use instructions, wording, and code patterns that make sense for a maintainer in 2000.
- `chapter-02/section-02` represents the year 2003.
- `chapter-02/section-03` represents the year 2004.
- `chapter-02/section-04` represents the year 2010.
- `chapter-02/section-05` represents the year 2016.
- `chapter-02/section-06` represents the year 2022.

Apply these rules to Chapter 02 section READMEs:

- Write for developers who want to work with that project in that era.
- Prefer commands, packaging terminology, and workflow assumptions that match the represented year.
- Do not use modern tools such as `uv`, `ruff`, `pyproject.toml`, or `python -m build` in older-era section READMEs unless the section actually contains those tools.
- Keep modern explanatory comparison and historical context in the MkDocs pages, not in the short section README.
- The section README should feel like a practical maintainer README from that time, not like a retrospective article.
- Still keep the README clear enough for today's junior developers to follow the example.

## MkDocs Configuration

Use a simple, maintainable MkDocs setup. Prefer this baseline unless the repository already has a different convention:

```yaml
site_name: Modern Python Engineering
site_description: Technical course notes for Python packaging and development environments.
nav:
  - Chapter 01:
      - Section 01: chapter-01/section-01.md
  - Chapter 02:
      - Section 01: chapter-02/section-01.md
theme:
  name: mkdocs
markdown_extensions:
  - admonition
  - tables
  - toc:
      permalink: true
```

Expand the `nav` list to include all actual sections. Keep the top-level navigation limited to `Chapter 01` and `Chapter 02`.

## Implementation Steps

1. Inspect the repository structure and all README files under root, `chapter-01/`, and `chapter-02/`.
2. Inspect each section's build/config files so command examples are accurate.
3. For Chapter 02 section READMEs, identify the represented year and write commands from that era's maintainer perspective.
4. Create `mkdocs.yml` and the `docs/` page tree.
5. Move the detailed educational explanation from section READMEs into the matching MkDocs pages.
6. Rewrite section READMEs into concise Usage Guide and Development Guide files.
7. Keep existing root and chapter README links working where reasonable.
8. Validate Markdown links and MkDocs navigation paths.
9. Run a lightweight validation command if available, such as:

```bash
mkdocs build --strict
```

If MkDocs is not installed, do not install packages unless explicitly asked. Instead, report the exact command that could not be run and why.

## Acceptance Criteria

- `mkdocs.yml` exists at the repository root.
- All documentation pages live under `docs/`.
- MkDocs top-level navigation contains only `Chapter 01` and `Chapter 02`.
- Each chapter's left navigation contains one entry per section named `Section 01`, `Section 02`, etc.
- The generated docs are based on existing README content and repository files.
- Section README files are short and follow `Usage Guide` / `Development Guide` structure.
- Commands shown in section READMEs are relevant and runnable for the section.
- Chapter 02 section READMEs are written from the perspective of maintainers working in each section's represented year.
- The documentation is direct, technically accurate, and suitable for junior developers.
- No unrelated code, Dockerfile, packaging, or helper-script behavior is changed.

## Final Response

When finished, summarize:

- created MkDocs files
- section READMEs that were simplified
- validation performed
- any validation that could not be performed
