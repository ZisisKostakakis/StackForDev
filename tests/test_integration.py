"""Integration tests — run against the live API.

These tests require a real network connection and a running API.
They are gated behind the INTEGRATION environment variable:

    RUN_INTEGRATION_TESTS=1 pytest -m integration

They are NOT run in CI on pull requests — only on pushes to main.
"""

import os

import pytest

from src.cli.api_client import generate_via_api
from src.generator_core import GenerateDockerfileRequest


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("RUN_INTEGRATION_TESTS"),
    reason="Set RUN_INTEGRATION_TESTS=1 to run integration tests",
)
class TestLiveAPI:
    """Tests that POST to the real StackForDev API endpoint."""

    def test_python_django_end_to_end(self):
        config = GenerateDockerfileRequest(
            language="python",
            dependency_stack="Django Stack",
            extra_dependencies=[],
            language_version="3.12",
        )
        result = generate_via_api(config)
        assert "dockerfile" in result
        assert "FROM python:3.12-bookworm" in result["dockerfile"]
        assert "key" in result
        assert result["key"].endswith(".dockerfile")

    def test_javascript_express_end_to_end(self):
        config = GenerateDockerfileRequest(
            language="javascript",
            dependency_stack="Express Stack",
            extra_dependencies=[],
            language_version="22",
        )
        result = generate_via_api(config)
        assert "dockerfile" in result
        assert "FROM node:22-bookworm" in result["dockerfile"]

    def test_go_gin_end_to_end(self):
        config = GenerateDockerfileRequest(
            language="go",
            dependency_stack="Gin Stack",
            extra_dependencies=[],
            language_version="1.23",
        )
        result = generate_via_api(config)
        assert "dockerfile" in result
        assert "FROM golang:1.23-bookworm" in result["dockerfile"]

    def test_response_has_required_fields(self):
        config = GenerateDockerfileRequest(
            language="python",
            dependency_stack="Flask Stack",
            extra_dependencies=["requests"],
            language_version="3.11",
        )
        result = generate_via_api(config)
        assert "dockerfile" in result
        assert "key" in result
        assert "message" in result
        assert "requests" in result["dockerfile"]
