import json
import shutil
import os
from unittest.mock import patch

import pytest

from src.generate_dockerfile import (
    lambda_handler,
    GenerateDockerfileRequest,
    DockerfileGenerator,
    generate_dockerfile_key_name,
    CORS_HEADERS,
)


def _make_event(config: dict) -> dict:
    return {
        "resource": "/generate-dockerfile",
        "path": "/generate-dockerfile",
        "httpMethod": "POST",
        "headers": {},
        "body": json.dumps({"config": config}),
        "isBase64Encoded": False,
    }


PYTHON_CONFIG = {
    "language": "python",
    "dependency_stack": "Django",
    "extra_dependencies": ["pandas", "numpy"],
    "language_version": "3.11",
}

JS_CONFIG = {
    "language": "JavaScript",
    "dependency_stack": "express",
    "extra_dependencies": ["cors", "dotenv"],
    "language_version": "20",
}

GO_CONFIG = {
    "language": "Go",
    "dependency_stack": "Gin Stack",
    "extra_dependencies": [],
    "language_version": "1.22",
}


@pytest.fixture(autouse=True)
def setup_env_and_cleanup(monkeypatch):
    monkeypatch.setenv("S3_BUCKET", "test-bucket")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    yield
    for d in ["python-images/", "javascript-images/", "go-images/"]:
        if os.path.isdir(d):
            shutil.rmtree(d)


# --- Happy path tests ---


def test_lambda_handler_python():
    result = lambda_handler(event=_make_event(PYTHON_CONFIG))
    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert "dockerfile" in body
    assert "FROM python:3.11-bullseye" in body["dockerfile"]
    assert "pip install django" in body["dockerfile"].lower()
    assert body["key"].startswith("dockerfile-python-Django-3.11")


def test_lambda_handler_javascript():
    result = lambda_handler(event=_make_event(JS_CONFIG))
    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert "FROM node:20-bullseye" in body["dockerfile"]
    assert "npm install -g express" in body["dockerfile"]


def test_lambda_handler_go():
    result = lambda_handler(event=_make_event(GO_CONFIG))
    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert "FROM golang:1.22-bullseye" in body["dockerfile"]
    assert "go install github.com/gin-gonic/gin" in body["dockerfile"]


def test_response_has_cors_headers():
    result = lambda_handler(event=_make_event(PYTHON_CONFIG))
    for key, value in CORS_HEADERS.items():
        assert result["headers"][key] == value


def test_response_has_dockerfile_content():
    result = lambda_handler(event=_make_event(PYTHON_CONFIG))
    body = json.loads(result["body"])
    assert "dockerfile" in body
    assert len(body["dockerfile"]) > 0


# --- Error path tests ---


def test_invalid_json_body():
    event = {
        "body": "not json",
    }
    result = lambda_handler(event=event)
    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert "error" in body


def test_missing_config_key():
    event = {
        "body": json.dumps({"wrong_key": {}}),
    }
    result = lambda_handler(event=event)
    assert result["statusCode"] == 400


def test_missing_required_fields():
    event = _make_event({"language": "python"})
    result = lambda_handler(event=event)
    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert "error" in body


def test_unsupported_language():
    config = {**PYTHON_CONFIG, "language": "Rust"}
    result = lambda_handler(event=_make_event(config))
    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert "Unsupported language" in body["error"]


def test_missing_env_vars(monkeypatch):
    monkeypatch.delenv("S3_BUCKET")
    monkeypatch.delenv("AWS_REGION")
    result = lambda_handler(event=_make_event(PYTHON_CONFIG))
    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert "S3_BUCKET" in body["error"]


# --- Input sanitization tests ---


def test_injection_semicolon_rejected():
    config = {**PYTHON_CONFIG, "extra_dependencies": ["pandas; rm -rf /"]}
    result = lambda_handler(event=_make_event(config))
    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert "error" in body


def test_injection_pipe_rejected():
    config = {**PYTHON_CONFIG, "extra_dependencies": ["pandas | cat /etc/passwd"]}
    result = lambda_handler(event=_make_event(config))
    assert result["statusCode"] == 400


def test_injection_backtick_rejected():
    config = {**PYTHON_CONFIG, "extra_dependencies": ["`whoami`"]}
    result = lambda_handler(event=_make_event(config))
    assert result["statusCode"] == 400


def test_injection_dollar_rejected():
    config = {**PYTHON_CONFIG, "extra_dependencies": ["$(whoami)"]}
    result = lambda_handler(event=_make_event(config))
    assert result["statusCode"] == 400


def test_injection_ampersand_rejected():
    config = {**PYTHON_CONFIG, "extra_dependencies": ["pandas && rm -rf /"]}
    result = lambda_handler(event=_make_event(config))
    assert result["statusCode"] == 400


def test_valid_version_specifier_accepted():
    config = {**PYTHON_CONFIG, "extra_dependencies": ["pandas>=1.5.0", "numpy[all]"]}
    result = lambda_handler(event=_make_event(config))
    assert result["statusCode"] == 200


# --- Template correctness tests ---


def test_python_template_structure():
    config = GenerateDockerfileRequest(**PYTHON_CONFIG)
    gen = DockerfileGenerator(config=config)
    content = gen.generate_dockerfile()
    assert "FROM python:3.11-bullseye" in content
    assert "WORKDIR /usr/src/app" in content
    assert 'CMD ["bash"]' in content


def test_javascript_template_structure():
    config = GenerateDockerfileRequest(**JS_CONFIG)
    gen = DockerfileGenerator(config=config)
    content = gen.generate_dockerfile()
    assert "FROM node:20-bullseye" in content
    assert "WORKDIR /usr/src/app" in content
    assert 'CMD ["bash"]' in content


def test_go_template_structure():
    config = GenerateDockerfileRequest(**GO_CONFIG)
    gen = DockerfileGenerator(config=config)
    content = gen.generate_dockerfile()
    assert "FROM golang:1.22-bullseye" in content
    assert "WORKDIR /usr/src/app" in content
    assert 'CMD ["bash"]' in content


def test_empty_extra_dependencies():
    config = {**PYTHON_CONFIG, "extra_dependencies": []}
    result = lambda_handler(event=_make_event(config))
    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert "pip install django" in body["dockerfile"].lower()


# --- Key name tests ---


def test_generate_key_name():
    config = GenerateDockerfileRequest(**PYTHON_CONFIG)
    key = generate_dockerfile_key_name(config)
    assert key == "dockerfile-python-Django-3.11-pandas-numpy.dockerfile"


def test_generate_key_name_no_extras():
    config = GenerateDockerfileRequest(**{**PYTHON_CONFIG, "extra_dependencies": []})
    key = generate_dockerfile_key_name(config)
    assert key == "dockerfile-python-Django-3.11-.dockerfile"


# --- S3 upload mock tests ---


@patch("src.generate_dockerfile.is_running_on_lambda", return_value=True)
@patch("src.generate_dockerfile.check_if_file_exists_in_s3", return_value=False)
@patch("src.generate_dockerfile.upload_to_s3")
def test_s3_upload_called_on_lambda(mock_upload, mock_exists, mock_lambda):
    result = lambda_handler(event=_make_event(PYTHON_CONFIG))
    assert result["statusCode"] == 200
    mock_upload.assert_called_once()


@patch("src.generate_dockerfile.is_running_on_lambda", return_value=True)
@patch("src.generate_dockerfile.check_if_file_exists_in_s3", return_value=True)
@patch("src.generate_dockerfile.upload_to_s3")
def test_s3_upload_skipped_when_exists(mock_upload, mock_exists, mock_lambda):
    result = lambda_handler(event=_make_event(PYTHON_CONFIG))
    assert result["statusCode"] == 200
    mock_upload.assert_not_called()


@patch("src.generate_dockerfile.is_running_on_lambda", return_value=True)
@patch("src.generate_dockerfile.check_if_file_exists_in_s3", return_value=False)
@patch("src.generate_dockerfile.upload_to_s3", side_effect=Exception("S3 error"))
def test_s3_upload_failure_returns_500(mock_upload, mock_exists, mock_lambda):
    result = lambda_handler(event=_make_event(PYTHON_CONFIG))
    assert result["statusCode"] == 500
    body = json.loads(result["body"])
    assert "S3 error" in body["error"]
