"""Tests for the API client using respx to mock httpx."""

import httpx
import pytest
import respx

from src.cli.api_client import generate_via_api
from src.cli.config import API_URL
from src.generator_core import GenerateDockerfileRequest


@pytest.fixture()
def config():
    return GenerateDockerfileRequest(
        language="python",
        dependency_stack="Django Stack",
        extra_dependencies=[],
        language_version="3.11",
    )


@respx.mock
def test_successful_api_call(config):
    respx.post(API_URL).mock(return_value=httpx.Response(
        200,
        json={"message": "ok", "key": "test.dockerfile", "dockerfile": "FROM python:3.11"},
    ))
    result = generate_via_api(config)
    assert result["dockerfile"] == "FROM python:3.11"


@respx.mock
def test_api_timeout_suggests_local(config):
    respx.post(API_URL).mock(side_effect=httpx.TimeoutException("timeout"))
    with pytest.raises(RuntimeError, match="--local"):
        generate_via_api(config)


@respx.mock
def test_api_connect_error_suggests_local(config):
    respx.post(API_URL).mock(side_effect=httpx.ConnectError("failed"))
    with pytest.raises(RuntimeError, match="--local"):
        generate_via_api(config)


@respx.mock
def test_api_http_error_shows_status(config):
    respx.post(API_URL).mock(return_value=httpx.Response(400, text="Bad Request"))
    with pytest.raises(RuntimeError, match="400"):
        generate_via_api(config)
