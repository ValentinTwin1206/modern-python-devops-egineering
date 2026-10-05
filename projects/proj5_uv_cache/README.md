# uv Cache Demo (ML Dependencies)

This project declares `tensorflow-cpu`, `transformers`, and `scikit-learn` in
`pyproject.toml`. The committed `uv.lock` pins their resolved dependencies.
The [uv cache workflow](../../.github/workflows/uv-cache.yml) installs them on
a fresh GitHub-hosted runner; it imports the packages but does not download
models or require a GPU.

To try it locally with Python 3.12 and uv installed, run from this directory:

```bash
uv sync --locked --python 3.12
.venv/bin/python -c "import tensorflow, transformers, sklearn; print('ML packages imported successfully')"
```

For the cross-run cache comparison and instructions, see
[Dependency Caching with uv](../../docs/chapter-03/section-03.md#try-the-cache-in-github-actions).
