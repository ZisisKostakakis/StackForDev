"""Tests for the generate CLI command."""

import json
import os

from click.testing import CliRunner

from src.cli.main import cli


runner = CliRunner()


def test_local_python_generates_dockerfile():
    result = runner.invoke(cli, ["generate", "--local", "-l", "python", "-s", "Django Stack", "-v", "3.11"])
    assert result.exit_code == 0
    assert "FROM python:3.11-bookworm" in result.output


def test_local_javascript_generates_dockerfile():
    result = runner.invoke(cli, ["generate", "--local", "-l", "javascript", "-s", "Express Stack", "-v", "20"])
    assert result.exit_code == 0
    assert "FROM node:20-bookworm" in result.output


def test_local_go_generates_dockerfile():
    result = runner.invoke(cli, ["generate", "--local", "-l", "go", "-s", "Gin Stack", "-v", "1.22"])
    assert result.exit_code == 0
    assert "FROM golang:1.22-bookworm" in result.output


def test_local_with_extras():
    result = runner.invoke(cli, [
        "generate", "--local", "-l", "python", "-s", "Django Stack", "-v", "3.11",
        "-e", "numpy,pandas",
    ])
    assert result.exit_code == 0
    assert "numpy" in result.output
    assert "pandas" in result.output


def test_output_flag_saves_file(tmp_path):
    outfile = str(tmp_path / "Dockerfile")
    result = runner.invoke(cli, [
        "generate", "--local", "-l", "python", "-s", "Django Stack", "-v", "3.11",
        "-o", outfile,
    ])
    assert result.exit_code == 0
    assert os.path.exists(outfile)
    with open(outfile) as f:
        content = f.read()
    assert "FROM python:3.11-bookworm" in content


def test_json_flag_outputs_json():
    result = runner.invoke(cli, [
        "generate", "--local", "-l", "python", "-s", "Django Stack", "-v", "3.11", "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["language"] == "python"
    assert data["stack"] == "Django Stack"
    assert "FROM python:3.11-bookworm" in data["dockerfile"]


def test_unsupported_language_error():
    result = runner.invoke(cli, ["generate", "--local", "-l", "cobol", "-s", "X", "-v", "1.0"])
    assert result.exit_code != 0
    assert "Unsupported language" in result.output


def test_local_rust_generates_dockerfile():
    result = runner.invoke(cli, ["generate", "--local", "-l", "rust", "-s", "Actix-Web Stack", "-v", "1.82"])
    assert result.exit_code == 0
    assert "FROM rust:1.82-bookworm" in result.output


def test_local_java_generates_dockerfile():
    result = runner.invoke(cli, ["generate", "--local", "-l", "java", "-s", "Spring Boot Stack", "-v", "21"])
    assert result.exit_code == 0
    assert "FROM eclipse-temurin:21-jdk-bookworm" in result.output


def test_unsupported_version_error():
    result = runner.invoke(cli, ["generate", "--local", "-l", "python", "-s", "Django Stack", "-v", "2.7"])
    assert result.exit_code != 0
    assert "Unsupported version" in result.output


def test_unsupported_stack_error():
    result = runner.invoke(cli, ["generate", "--local", "-l", "python", "-s", "FakeStack", "-v", "3.11"])
    assert result.exit_code != 0
    assert "Unsupported stack" in result.output


def test_missing_flags_non_tty_error():
    """CliRunner is non-TTY by default, so missing flags should error."""
    result = runner.invoke(cli, ["generate", "--local"])
    assert result.exit_code != 0
    assert "--language" in result.output


def test_version_option():
    from importlib.metadata import version
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert version("stackfordev") in result.output


def test_compose_flag_outputs_compose_content():
    result = runner.invoke(cli, [
        "generate", "--local", "-l", "python", "-s", "Django Stack", "-v", "3.11", "--compose",
    ])
    assert result.exit_code == 0
    assert "docker-compose.yml" in result.output or "services:" in result.output
    assert "volumes:" in result.output


def test_compose_flag_with_output_creates_files(tmp_path):
    outfile = str(tmp_path / "Dockerfile")
    result = runner.invoke(cli, [
        "generate", "--local", "-l", "python", "-s", "Django Stack", "-v", "3.11",
        "--compose", "-o", outfile,
    ])
    assert result.exit_code == 0
    assert os.path.exists(outfile)
    assert os.path.exists(str(tmp_path / "docker-compose.yml"))
    assert os.path.exists(str(tmp_path / ".dockerignore"))

    with open(str(tmp_path / "docker-compose.yml")) as f:
        compose = f.read()
    assert "services:" in compose
    assert "/usr/src/app" in compose

    with open(str(tmp_path / ".dockerignore")) as f:
        dockerignore = f.read()
    assert "__pycache__" in dockerignore
    assert "node_modules" in dockerignore
