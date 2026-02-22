"""Tests for the stackfordev init command."""

import os

import pytest
from click.testing import CliRunner

from src.cli.main import cli

runner = CliRunner()


def test_init_creates_all_files(tmp_path):
    result = runner.invoke(cli, [
        "init", "-l", "python", "-s", "Django Stack", "-v", "3.12", "-d", str(tmp_path),
    ])
    assert result.exit_code == 0, result.output

    assert os.path.exists(tmp_path / "Dockerfile")
    assert os.path.exists(tmp_path / "docker-compose.yml")
    assert os.path.exists(tmp_path / ".dockerignore")
    assert os.path.exists(tmp_path / "devrun.sh")


def test_init_dockerfile_has_correct_content(tmp_path):
    runner.invoke(cli, [
        "init", "-l", "python", "-s", "Django Stack", "-v", "3.12", "-d", str(tmp_path),
    ])
    with open(tmp_path / "Dockerfile") as f:
        content = f.read()
    assert "FROM python:3.12-bookworm" in content
    assert "django" in content.lower()


def test_init_compose_has_volume_mount(tmp_path):
    runner.invoke(cli, [
        "init", "-l", "javascript", "-s", "Express Stack", "-v", "22", "-d", str(tmp_path),
    ])
    with open(tmp_path / "docker-compose.yml") as f:
        content = f.read()
    assert "services:" in content
    assert "/usr/src/app" in content
    assert "volumes:" in content


def test_init_dockerignore_has_standard_entries(tmp_path):
    runner.invoke(cli, [
        "init", "-l", "go", "-s", "Gin Stack", "-v", "1.23", "-d", str(tmp_path),
    ])
    with open(tmp_path / ".dockerignore") as f:
        content = f.read()
    assert "__pycache__" in content
    assert "node_modules" in content
    assert ".env" in content


def test_init_devrun_sh_has_docker_compose_run(tmp_path):
    runner.invoke(cli, [
        "init", "-l", "rust", "-s", "Actix-Web Stack", "-v", "1.82", "-d", str(tmp_path),
    ])
    with open(tmp_path / "devrun.sh") as f:
        content = f.read()
    assert "docker compose run" in content
    assert "devrun" in content


def test_init_missing_flags_non_tty_errors():
    result = runner.invoke(cli, ["init"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_init_with_extras_included_in_dockerfile(tmp_path):
    runner.invoke(cli, [
        "init", "-l", "python", "-s", "Data Science Stack", "-v", "3.11",
        "-e", "seaborn,plotly", "-d", str(tmp_path),
    ])
    with open(tmp_path / "Dockerfile") as f:
        content = f.read()
    assert "seaborn" in content
    assert "plotly" in content
