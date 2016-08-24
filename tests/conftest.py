import pytest
from py.path import local
from peewee import SqliteDatabase
from playhouse.test_utils import test_database
from click.testing import CliRunner

from pokediadb import models
from pokediadb.enums import Lang


# pylint: disable=W0621


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


@pytest.fixture
def db():
    models.db.init(":memory:")
    models.db.connect()
    models.db.create_tables([models.Language, models.DamageClass])

    # Create languages
    languages = {
        Lang.fr: models.Language.create(code="fr", name="Français"),
        Lang.en: models.Language.create(code="en", name="English"),
    }

    # Create damage class
    models.DamageClass.get_or_create(id=1, name="Status", image="status.png")
    models.DamageClass.get_or_create(
        id=2, name="Physical", image="physical.png"
    )
    models.DamageClass.get_or_create(id=3, name="Special", image="special.png")

    return models.db, languages


@pytest.fixture
def version_test_data(tmp_context):
    test_db = SqliteDatabase(tmp_context.join("data/test_data.sql").strpath)
    with test_database(test_db, (
        models.Language, models.Version, models.VersionTranslation
    ), create_tables=False):
        return (
            list(models.Version.select()),
            list(models.VersionTranslation.select())
        )


@pytest.fixture
def type_test_data(tmp_context):
    test_db = SqliteDatabase(tmp_context.join("data/test_data.sql").strpath)
    with test_database(test_db, (
        models.Language, models.Type, models.TypeEfficacy,
        models.TypeTranslation
    ), create_tables=False):
        return (
            list(models.Type.select()),
            list(models.TypeEfficacy.select()),
            list(models.TypeTranslation.select())
        )


@pytest.fixture
def ability_test_data(tmp_context):
    test_db = SqliteDatabase(tmp_context.join("data/test_data.sql").strpath)
    with test_database(test_db, (
        models.Language, models.Ability, models.AbilityTranslation
    ), create_tables=False):
        return (
            list(models.Ability.select()),
            sorted(
                list(models.AbilityTranslation.select()),
                key=lambda x: (x.ability.id, x.lang)
            )
        )


@pytest.fixture
def move_test_data(tmp_context):
    test_db = SqliteDatabase(tmp_context.join("data/test_data.sql").strpath)
    with test_database(test_db, (
        models.Language, models.Move, models.MoveTranslation
    ), create_tables=False):
        return (
            list(models.Move.select()),
            sorted(
                list(models.MoveTranslation.select()),
                key=lambda x: (x.move.id, x.lang)
            )
        )


@pytest.fixture
def pkm_test_data(tmp_context):
    test_db = SqliteDatabase(tmp_context.join("data/test_data.sql").strpath)
    with test_database(test_db, (
        models.Language, models.Pokemon, models.PokemonTranslation,
        models.PokemonAbility
    ), create_tables=False):
        return (
            list(models.Pokemon.select()),
            list(models.PokemonTranslation.select()),
            list(models.PokemonAbility.select())
        )
