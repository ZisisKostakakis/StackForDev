# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Rust language support (Actix-Web Stack, CLI Tools Stack, WebAssembly Stack)
- Java language support (Spring Boot Stack, Maven Build Stack, Gradle Build Stack)
- `--compose` flag: generates `docker-compose.yml` and `.dockerignore` alongside Dockerfile
- `stackfordev info` subcommand: shows all supported languages, versions, and stacks in a Rich table
- GitHub Actions CI workflow: runs tests and lint on every push and pull request to `main`
- Codecov coverage reporting and badge
- CloudWatch alarms for Lambda error rate and throttles
- CloudWatch log group with 30-day retention and structured JSON logging
- S3 lifecycle policy: STANDARD_IA after 90 days, expiry after 365 days
- Lambda `reserved_concurrent_executions = 10` for cost safety
- `language_version` field validator in Pydantic model (cross-checks against valid versions per language)
- CONTRIBUTING.md with setup guide and language addition walkthrough
- CHANGELOG.md

### Changed
- Upgraded base Docker images from `bullseye` to `bookworm` (all languages)
- PyPI classifier updated from `3 - Alpha` to `4 - Beta`

### Fixed
- `generate_dockerfile_key_name` no longer produces a trailing dash when `extra_dependencies` is empty

## [0.1.4] — 2025-01-01

### Changed
- Version bump

## [0.1.3] — 2025-01-01

### Changed
- Version bump

## [0.1.2] — 2024-12-01

### Added
- Licensing and PyPI documentation

## [0.1.1] — 2024-11-01

### Added
- CLI package and PyPI publish workflow
- Lambda API body now accepts JSON format

## [0.1.0] — 2024-10-01

### Added
- Initial release
- AWS Lambda backend with API Gateway
- Python, JavaScript, and Go Dockerfile generation
- Click CLI with interactive and non-interactive modes
- S3 storage with deduplication
- Terraform IaC (Lambda, API Gateway, ECR, S3, IAM)
