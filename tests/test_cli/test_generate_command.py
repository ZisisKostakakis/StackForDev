"""Tests for the generate CLI command."""

import json
import os

from click.testing import CliRunner

from src.cli.main import cli


runner = CliRunner()


def test_local_python_generates_dockerfile():
    result = runner.invoke(cli, ["generate", "--local", "-l", "python", "-s", "Django Stack", "-v", "3.11"])
    assert result.exit_code == 0
    assert "FROM python:3.11-bullseye" in result.output


def test_local_javascript_generates_dockerfile():
    result = runner.invoke(cli, ["generate", "--local", "-l", "javascript", "-s", "Express Stack", "-v", "20"])
    assert result.exit_code == 0
    assert "FROM node:20-bullseye" in result.output


def test_local_go_generates_dockerfile():
    result = runner.invoke(cli, ["generate", "--local", "-l", "go", "-s", "Gin Stack", "-v", "1.22"])
    assert result.exit_code == 0
    assert "FROM golang:1.22-bullseye" in result.output


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
    assert "FROM python:3.11-bullseye" in content


def test_json_flag_outputs_json():
    result = runner.invoke(cli, [
        "generate", "--local", "-l", "python", "-s", "Django Stack", "-v", "3.11", "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["language"] == "python"
    assert data["stack"] == "Django Stack"
    assert "FROM python:3.11-bullseye" in data["dockerfile"]


def test_unsupported_language_error():
    result = runner.invoke(cli, ["generate", "--local", "-l", "rust", "-s", "X", "-v", "1.0"])
    assert result.exit_code != 0
    assert "Unsupported language" in result.output


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
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output
