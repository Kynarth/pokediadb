import pytest
import peewee

from pokediadb import models
from pokediadb.enums import Lang
from pokediadb.database import db_init
from pokediadb.database import build_moves
from pokediadb.database import build_types
from pokediadb.database import build_pokemons
from pokediadb.database import build_versions
from pokediadb.database import build_abilities


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
    err_info.match(r"unable to open database file")


def test_database_initialization_with_already_existing_file(tmp_context):
    db_file = tmp_context.join("data/test_data.sql")
    with pytest.raises(FileExistsError) as err_info:
        _, _ = db_init(db_file.strpath)
    err_info.match(
        r"The database '{}' already exist.".format(
            db_file.strpath.replace("\\", r"\\"))
    )


def test_pokemon_versions_data_collection(tmp_context, db, version_test_data):
    csv = tmp_context.join("data/csv")
    build_versions(*db, csv.strpath)

    assert version_test_data == (
        list(models.Version.select()),
        list(models.VersionTranslation.select())
    )


def test_pokemon_types_data_collection(tmp_context, db, type_test_data):
    csv = tmp_context.join("data/csv")
    build_types(*db, csv.strpath)

    assert type_test_data == (
        list(models.Type.select()), list(models.TypeEfficacy.select()),
        sorted(
            list(models.TypeTranslation.select()),
            key=lambda x: (x.type.id, x.lang)
        )
    )


def test_pokemon_abilities_data_collection(tmp_context, db, ability_test_data):
    csv = tmp_context.join("data/csv")
    build_abilities(*db, csv.strpath)

    assert ability_test_data == (
        list(models.Ability.select()),
        sorted(
            list(models.AbilityTranslation.select()),
            key=lambda x: (x.ability.id, x.lang)
        ),
    )


def test_moves_data_collection(tmp_context, db, move_test_data):
    csv = tmp_context.join("data/csv")
    build_types(*db, csv.strpath)
    build_moves(*db, csv.strpath)

    assert move_test_data == (
        list(models.Move.select()),
        sorted(
            list(models.MoveTranslation.select()),
            key=lambda x: (x.move.id, x.lang)
        )
    )


def test_pokemon_data_collection(tmp_context, db, pkm_test_data):
    csv = tmp_context.join("data/csv")
    build_abilities(*db, csv.strpath)
    build_pokemons(*db, csv.strpath)

    assert pkm_test_data == (
        list(models.Pokemon.select()),
        sorted(
            list(models.PokemonTranslation.select()),
            key=lambda x: (x.pokemon.id, x.lang)
        ),
        list(models.PokemonAbility.select())
    )
