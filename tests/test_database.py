import pytest
import peewee

from pokediadb import models
from pokediadb.enums import Lang
from pokediadb.database import db_init
from pokediadb.database import build_types
from pokediadb.database import build_abilities
from pokediadb.database import build_pokemons
from pokediadb.database import build_moves
from pokediadb.database import build_versions


def test_database_initialization_with_correct_path(tmp_context):
    db_file = tmp_context.mkdir("database_test").join("pokemon.sql")
    db, languages = db_init(db_file.strpath)
    assert db.database == db_file.strpath

    for lang in Lang.__members__.values():
        assert lang in languages.keys()


def test_database_initialization_with_incorrect_path(tmp_context):
    directory = tmp_context.join("pokemon")
    db_file = directory.join("wrong_file.sql")
    assert directory.check(exists=0)

    with pytest.raises(peewee.OperationalError) as err_info:
        _, _ = db_init(str(db_file))
    assert str(err_info.value) == "unable to open database file"


def test_database_initialization_with_already_existing_file(tmp_context):
    first_file = tmp_context.join("first.sql")
    first_file.write("test")
    assert first_file.check(file=1)

    with pytest.raises(FileExistsError) as err_info:
        _, _ = db_init(str(first_file))
    assert str(err_info.value) == (
        "The file '{}' already exists.".format(str(first_file))
    )


def test_pokemon_versions_data_collection(tmp_context):
    db_file = tmp_context.mkdir("database_test").join("pokemon.sql")
    csv = tmp_context.join("data/csv")
    db, languages = db_init(db_file.strpath)
    build_versions(db, languages, csv.strpath)

    assert db_file.check(file=1)
    assert len(models.Version.select()) == 26
    assert len(models.VersionTranslation.select()) == 52


def test_pokemon_types_data_collection(tmp_context):
    db_file = tmp_context.mkdir("database_test").join("pokemon.sql")
    csv = tmp_context.join("data/csv")
    db, languages = db_init(db_file.strpath)
    build_types(db, languages, csv.strpath)

    assert db_file.check(file=1)
    assert len(models.Type.select()) == 3
    assert len(models.TypeEfficacy.select()) == 9
    assert len(models.TypeTranslation.select()) == 6


def test_pokemon_abilities_data_collection(tmp_context):
    db_file = tmp_context.mkdir("database_test").join("pokemon.sql")
    csv = tmp_context.join("data/csv")
    db, languages = db_init(db_file.strpath)
    build_abilities(db, languages, csv.strpath)

    assert db_file.check(file=1)
    assert len(models.Ability.select()) == 8
    assert len(models.AbilityTranslation.select()) == 16


def test_moves_data_collection(tmp_context):
    db_file = tmp_context.mkdir("database_test").join("pokemon.sql")
    csv = tmp_context.join("data/csv")
    db, languages = db_init(db_file.strpath)

    build_types(db, languages, csv.strpath)
    build_moves(db, languages, csv.strpath)

    assert db_file.check(file=1)
    assert len(models.Move.select()) == 6
    assert len(models.MoveTranslation.select()) == 12


def test_pokemon_data_collection(tmp_context):
    db_file = tmp_context.mkdir("database_test").join("pokemon.sql")
    csv = tmp_context.join("data/csv")
    db, languages = db_init(db_file.strpath)

    build_abilities(db, languages, csv.strpath)
    build_pokemons(db, languages, csv.strpath)

    assert db_file.check(file=1)
    assert len(models.Pokemon.select()) == 6
    assert len(models.PokemonAbility.select()) == 12
    assert len(models.PokemonTranslation.select()) == 12
