# Contributing to StackForDev

## Local Setup

```bash
git clone https://github.com/ZisisKostakakis/StackForDev.git
cd StackForDev
pip install poetry
poetry install --with dev
```

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=term-missing

# Single test
pytest tests/test_generate_dockerfile.py::test_lambda_handler_python
```

## Linting

```bash
pylint src/
```

## Adding a New Language

Adding a language requires changes to **4 files**:

1. **`src/docker_templates/<language>_template.py`** — Create the Dockerfile template with `START_OF_TEMPLATE`, `END_OF_TEMPLATE`, and a version placeholder (e.g. `RUST_VERSION`).

2. **`src/generator_core.py`** — Add an entry to `TEMPLATE_REGISTRY` and stacks to `STACK_PACKAGES`.

3. **`src/cli/config.py`** — Add the language's versions to `LANGUAGE_VERSIONS` and stacks to `LANGUAGE_STACKS`.

4. **`tests/test_generate_dockerfile.py`** — Add a `test_lambda_handler_<language>` test and a `test_<language>_template_structure` test.

## Pull Request Process

1. Branch protection requires CI to pass before merging to `main`.
2. Run `pytest` and `pylint src/` locally before pushing.
3. Update `CHANGELOG.md` under `[Unreleased]`.
4. Open a PR with a clear description of what changed and why.

## Branch Protection

The `main` branch requires all CI status checks to pass (tests + lint) before a PR can be merged.
