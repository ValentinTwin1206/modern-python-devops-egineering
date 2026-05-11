# Copilot Instructions

This repository contains teaching material for modern Python engineering. When editing MkDocs documentation, write for a technical but not yet experienced audience. Be friendly, direct, and practical. Prefer clear explanations over jargon, and introduce terms before relying on them.

## Documentation Style

- Use Chicago style for capitalization, punctuation, and prose mechanics where it does not conflict with technical correctness.
- Keep explanations concise, but include enough background for junior developers to understand why a workflow exists.
- Use consistent section structure within each chapter. When one section in a chapter introduces a layout pattern, apply the same pattern to the sibling sections unless the content clearly needs a different shape.
- Prefer a short `Used Project` section near the top of each section page. Include a compact table for the relevant tools, files, and project components.
- Link tool names to official documentation when useful and stable.
- Keep step-by-step workflow commands in the section README when the MkDocs page is meant to explain concepts. Link to the README instead of duplicating long command sequences.

## MkDocs Layout

- Use MkDocs Material features idiomatically: admonitions for important context, tables for compact comparisons, and tabs for equivalent command variants.
- Prefer tabs when comparing commands for different tools, such as `pip install` and `uv pip install`.
- Use one command per code block when a command sequence needs explanation. Add a short sentence before each code block.
- Use fenced code blocks with accurate language identifiers, such as `bash`, `python`, `yaml`, `toml`, `ini`, or `text`.
- Preserve indentation inside code blocks exactly, especially for YAML, TOML, filesystem trees, and nested MkDocs tab content.

## Chapter 01 Layout

- Start each Chapter 01 section page with a concise introduction, then a level-two example-project section. Sections 01 and 02 use `Tiny Webserver Project`. Section 03 (Conda) uses `Image Processor Project` (OpenCV + NumPy showcase). Section 04 (Pipenv) uses `FastAPI CRUD Project` (FastAPI + Pydantic + uvicorn showcase). Section 05 (Dev Containers) uses `Pixelpack Project` (Pillow + Click + Nuitka showcase). Use the matching project name as the level-two heading on each page.
- In Chapter 01, split that example-project section into level-three `Used DevTools` and `Project Files` subsections.
- Start each of those subsections with a short sentence that explains what the table covers.
- In Chapter 01, both tables should use the columns `Component` and `Description`.
- Write the description column as short, direct prose. Prefer about two sentences per component so the description can cover both what the component is and why it matters in that section.
- Cross-reference important project files directly, especially `Dockerfile`, `Dockerfile.devEnv`, `.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`, `pyproject.toml`, `environment.yml`, `Pipfile`, and `Pipfile.lock`.
- Except for Chapter 01, Section 01, add a level-two ``Install {environment}`` section after the example-project section, such as ``Install `venv````, ``Install `Conda````, ``Install `Pipenv````, or ``Install `Dev Container```.
- When an environment tool is bundled with Python, such as `venv`, say so directly before showing any operating-system package needed on Debian-based systems.
- Keep each `Install {environment}` section limited to installing the tool itself. Move environment creation, activation, and startup commands into the later workflow or container-entrypoint section.
- After `Install {environment}` and before `Workflow`, use a level-two ``{environment}` environment model` section. Put the concise explanation directly under that heading instead of adding a separate `Summary` subheading.
- Keep environment-model details, such as layout, dependency files, image overview, entrypoints, and runtimes, as level-three headings under `{environment} environment model` when they appear before `Workflow`.

## Content Accuracy

- Verify generated filesystem trees, command output, package layouts, and tool behavior against the repository or a real command when feasible.
- Distinguish between clean baseline environments and project environments after dependencies are installed.
- Avoid implying that Docker, Conda, `venv`, Pipenv, or system Python behave the same unless the page explicitly explains the difference.
- Do not replace user-facing project workflow instructions in READMEs with long duplicated MkDocs sections; cross-reference instead.
