from peewee import SqliteDatabase

from pokediadb import log
from pokediadb.cli import pokediadb
from pokediadb.models import Type, TypeEfficacy, TypeTranslation


def test_database_generation_without_args(runner, tmp_context):
    result = runner.invoke(pokediadb, ["generate", "-v"])
    assert result.exit_code == 0

    # Check existence of the database and the csv and sprites folders
    db_file = tmp_context.join("pokediadb.sql")
    assert db_file.check(file=1)
    assert tmp_context.join("csv").check(dir=1)
    assert tmp_context.join("sprites").check(dir=1)

    # Check type tables
    db = SqliteDatabase(str(db_file))
    db.connect()
    assert len(Type.select()) == 18
    assert len(TypeEfficacy.select()) == 324
    assert len(TypeTranslation.select()) == 36


def test_database_generation_with_csv_and_sprites(runner):
    result = runner.invoke(pokediadb, ["download", "-v"])
    result = runner.invoke(pokediadb, ["generate", "-v"])
    assert result.exit_code == 0


def test_database_generation_with_args(runner, tmp_context):
    db_dir = tmp_context.mkdir("database")
    result = runner.invoke(
        pokediadb, ["generate", "-v", "database", "-n", "test.sqlite3"]
    )
    assert result.exit_code == 0

    assert db_dir.join("test.sqlite3").check(file=1)
    assert db_dir.join("csv").check(dir=1)
    assert db_dir.join("sprites").check(dir=1)


def test_database_generation_with_invalid_path(runner):
    result = runner.invoke(pokediadb, ["generate", "-v", "wrong_path"])
    assert result.exit_code == 2
    assert 'Error: Invalid value for "path":' in result.output


def test_database_generation_with_existent_sql_file(runner, tmp_context):
    sql_file = tmp_context.join("pokediadb.sql")
    sql_file.write("test")
    result = runner.invoke(pokediadb, ["generate", "-v"])
    print(result.output)
    assert result.exit_code == 1
    assert log.error(
        "The file '{}' already exists".format(sql_file)) in result.output


def test_database_generation_with_invalid_names(runner):
    # Forbidden character
    result = runner.invoke(pokediadb, ["generate", "-v", "-n", "/test.sql"])
    assert result.exit_code == 2
    assert "Invalid file name" in result.output

    # Several extensions
    result = runner.invoke(pokediadb, ["generate", "-v", "-n", "test.db.sql"])
    assert result.exit_code == 2
    assert "Invalid file name" in result.output

    # No extension
    result = runner.invoke(pokediadb, ["generate", "-v", "-n", "test"])
    assert result.exit_code == 0

    # Invalid extension
    result = runner.invoke(pokediadb, ["generate", "-v", "-n", "test.aze"])
    assert result.exit_code == 2
