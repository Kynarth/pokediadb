import pytest
from py.path import local

from click.testing import CliRunner


@pytest.fixture
def runner():
    """Allow invoking command as command line scripts in isolation."""
    return CliRunner()


@pytest.yield_fixture(autouse=True)
def tmp_context():
    """Create an isolated file system for tests with its test data."""
    with CliRunner().isolated_filesystem():
        data_dir = local(local(__file__).dirname).join("data")
        data_dir.copy(local("data").mkdir())
        yield local(".")
