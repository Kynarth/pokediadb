from pokediadb import cli


def test_cli(runner):
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Hello, world.'


def test_cli_with_arg(runner):
    result = runner.invoke(cli.main, ['Kynarth'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Hello, Kynarth.'
