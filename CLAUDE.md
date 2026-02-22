# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run tests
pytest

# Run a single test
pytest tests/test_generate_dockerfile.py::test_name

# Build Lambda container image
make build

# Full deploy (build → ECR push → Lambda update)
make deploy

# Lint
pylint src/
```

Dependencies are managed with **Poetry** (`pyproject.toml`). Source root is `src/` (set as `pythonpath` in pyproject.toml for pytest).

## Architecture

AWS Lambda service that generates Dockerfiles from templates and stores them in S3. Exposed via API Gateway (regional, API key auth). This is the **backend** for the SvelteKit frontend at `../StackForDev-FrontEnd/`.

**Request flow:**
```
POST /generate-dockerfile (API Gateway + x-api-key)
  → lambda_handler (src/generate_dockerfile.py)
  → GenerateDockerfileRequest (Pydantic validation)
  → DockerfileGenerator.generate() → template substitution
  → S3 dedup check → upload
  → JSON response {statusCode, message, key, url}
```

**API request body:**
```json
{
  "config": {
    "language": "Python",
    "dependency_stack": "Django Stack",
    "extra_dependencies": ["numpy", "pandas"],
    "language_version": "3.11"
  }
}
```

**Key files:**
- `src/generate_dockerfile.py` — Lambda handler, `GenerateDockerfileRequest` Pydantic model, `DockerfileGenerator` class
- `src/s3_helper.py` — S3 upload and existence check
- `src/docker_templates/python_template.py` — Dockerfile template string with placeholders (`PYTHON_VERSION`, `DEPENDENCY_STACK`, `EXTRA_DEPENDENCIES`)
- `aws_resources/` — Terraform IaC (Lambda, API Gateway, ECR, S3, IAM)
- `generate_dockerfile.dockerfile` — Lambda container image definition (Python 3.11 base)

**S3 key format:** `python-images/dockerfile-{language}-{dependency_stack}-{language_version}-{extra_dependencies}.dockerfile`

**Infrastructure:** Terraform Cloud workspace "StackForDev", AWS provider ~> 5.0. Lambda runs as ECR container image with 30s timeout.

## Project Vision

StackForDev enables **Docker-as-dev-environment**: developers only need Docker installed. They select a language + stack via the frontend UI, the backend generates a tailored Dockerfile, and the resulting container acts as a transparent runtime proxy — so commands like `python script.py` run inside the container against the project's volume-mounted files, with no local language/dependency installation required.
