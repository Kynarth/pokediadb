import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    """Allow invoking command as command line scripts in isolation."""
    return CliRunner()
