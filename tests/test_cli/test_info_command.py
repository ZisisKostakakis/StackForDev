"""Tests for the info CLI command."""

from click.testing import CliRunner

from src.cli.main import cli

runner = CliRunner()


def test_info_shows_all_languages():
    result = runner.invoke(cli, ["info"])
    assert result.exit_code == 0
    for lang in ["python", "javascript", "go", "rust", "java"]:
        assert lang in result.output


def test_info_shows_versions():
    result = runner.invoke(cli, ["info"])
    assert result.exit_code == 0
    assert "3.12" in result.output
    assert "1.82" in result.output
    assert "21" in result.output


def test_info_shows_stacks():
    result = runner.invoke(cli, ["info"])
    assert result.exit_code == 0
    assert "Django Stack" in result.output
    assert "Actix-Web Stack" in result.output
    assert "Spring Boot Stack" in result.output
