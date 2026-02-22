# StackForDev

[![CI](https://github.com/ZisisKostakakis/StackForDev/actions/workflows/ci.yml/badge.svg)](https://github.com/ZisisKostakakis/StackForDev/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/stackfordev.svg)](https://badge.fury.io/py/stackfordev)
[![Python Versions](https://img.shields.io/pypi/pyversions/stackfordev)](https://pypi.org/project/stackfordev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![codecov](https://codecov.io/gh/ZisisKostakakis/StackForDev/branch/main/graph/badge.svg)](https://codecov.io/gh/ZisisKostakakis/StackForDev)

> **Docker as your dev environment.** Select a language and stack, get a tailored Dockerfile — no local language installation required.

Instead of installing Python, Node, Go, Rust, or Java on your machine, StackForDev generates a Dockerfile that acts as a transparent runtime proxy. You run commands _inside_ the container against your volume-mounted project files. Your host stays clean.

## Quick Start

```bash
pip install stackfordev

# Bootstrap a complete dev workspace in one command
stackfordev init -l python -s "Django Stack" -v 3.12

# Then:
docker compose build
source devrun.sh
devrun python manage.py runserver
```

Or just generate a Dockerfile:

```bash
stackfordev generate -l python -s "Django Stack" -v 3.12 --compose -o ./Dockerfile
```

## Usage

```bash
# Bootstrap a full workspace (Dockerfile + docker-compose.yml + .dockerignore + devrun.sh)
stackfordev init -l python -s "Django Stack" -v 3.12
stackfordev init  # interactive mode

# Interactive mode (prompts for missing options)
stackfordev generate

# Non-interactive
stackfordev generate -l python -s "Django Stack" -v 3.12

# With extra dependencies
stackfordev generate -l python -s "Data Science Stack" -v 3.11 -e "numpy,pandas,scikit-learn"

# Save to file
stackfordev generate -l go -s "Gin Stack" -v 1.23 -o ./Dockerfile

# Also generate docker-compose.yml and .dockerignore
stackfordev generate -l python -s "Django Stack" -v 3.12 --compose -o ./Dockerfile

# Generate offline (no API call)
stackfordev generate -l javascript -s "Express Stack" -v 22 --local

# Raw JSON output
stackfordev generate -l rust -s "Actix-Web Stack" -v 1.82 --json

# Show all supported languages, versions, and stacks
stackfordev info
```

## Supported Languages & Stacks

Use `stackfordev info` for a live table. Summary:

| Language   | Versions              | Stacks |
|------------|-----------------------|--------|
| Python     | 3.9, 3.10, 3.11, 3.12 | Django Stack, Flask Stack, Data Science Stack, Web Scraping Stack, Machine Learning Stack |
| JavaScript | 18, 20, 22            | Express Stack, React Stack, Vue.js Stack, Node.js API Stack, Full-Stack JavaScript |
| Go         | 1.21, 1.22, 1.23      | Gin Stack, Beego Stack, Web Framework Stack, Microservices Stack, Data Processing Stack |
| Rust       | 1.80, 1.81, 1.82      | Actix-Web Stack, CLI Tools Stack, WebAssembly Stack |
| Java       | 11, 17, 21            | Spring Boot Stack, Maven Build Stack, Gradle Build Stack |

## CLI Options

```
stackfordev generate [OPTIONS]

  -l, --language TEXT    Programming language
  -s, --stack TEXT       Dependency stack (e.g. 'Django Stack')
  -v, --version TEXT     Language version (e.g. 3.12)
  -e, --extras TEXT      Comma-separated extra dependencies
  -o, --output PATH      Save Dockerfile to path
  --compose              Also generate docker-compose.yml and .dockerignore
  --local                Generate offline without API call
  --json                 Output raw JSON response
  --help                 Show this message and exit.

stackfordev info        Show supported languages, versions, and stacks

stackfordev init [OPTIONS]

  -l, --language TEXT    Programming language
  -s, --stack TEXT       Dependency stack
  -v, --version TEXT     Language version
  -e, --extras TEXT      Comma-separated extra dependencies
  -d, --directory PATH   Target directory (default: current directory)
  --help                 Show this message and exit.
```

## How It Works

1. Select language, stack, and version (interactively or via flags)
2. The CLI calls the StackForDev API, or generates locally with `--local`
3. A tailored Dockerfile (and optionally `docker-compose.yml` + `.dockerignore`) is returned
4. Build the image and run commands inside the container — no local language installation needed

## Architecture

![Architecture Diagram](https://raw.githubusercontent.com/ZisisKostakakis/StackForDev/main/images/StackForDev.png)

**Request flow:**

```
CLI / API call
  → API Gateway (rate-limited, CORS)
  → AWS Lambda (Python 3.11, container runtime, ECR)
  → Pydantic validation + injection checks
  → Template substitution (language + stack + version)
  → S3 dedup check → upload
  → JSON response {dockerfile, key, message}
```

**Infrastructure:** AWS Lambda + API Gateway + S3 + ECR, provisioned with Terraform. CloudWatch alarms monitor error rate and throttles. S3 lifecycle policy manages storage costs automatically.

## Monitoring

- **Errors alarm:** fires when Lambda errors ≥ 5 in a 5-minute window → SNS notification
- **Throttles alarm:** fires when Lambda throttles ≥ 10 in a 5-minute window
- **Log retention:** CloudWatch Logs retained for 30 days, structured as JSON for Logs Insights queries
- **Concurrency cap:** Lambda reserved concurrency set to 10 to prevent runaway scaling

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for local setup, how to run tests, and how to add a new language template in 4 steps.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT — see [LICENSE](LICENSE) for details.
