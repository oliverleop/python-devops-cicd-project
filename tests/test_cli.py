from click.testing import CliRunner

from simple_http_checker.cli import main


def test_no_urls():
    runner = CliRunner()
    result = runner.invoke(main, [])

    assert result.exit_code == 0
    assert "Please provide at least one URL to check." in result.output
