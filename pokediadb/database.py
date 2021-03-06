"""Helper functions with database."""

import os
from pathlib import Path

import click

from pokediadb import log
from pokediadb import models
from pokediadb.enums import Lang
from pokediadb.utils import max_sql_variables
from pokediadb import dbuilder


SQLITE_LIMIT_VARIABLE_NUMBER = max_sql_variables()


def get_max_size(data):
    """Get the maximum of numbers rows from data to be used in one time.

    Args:
        data (list): List of dict containing infos to build a
            pokediadb.models object.

    Returns:
        int: Max number of data's row.

    """
    if data:
        return (SQLITE_LIMIT_VARIABLE_NUMBER // len(data[0])) - 1
    else:
        log.error("Provided an empty data list to get_max_size function.")
        raise click.Abort()


def db_init(path):
    """Initialize pokémon database with the given name.

    Args:
        path (str): Path the sqlite database file.

    Returns:
        peewee.SqliteDatabase : Database instance.
        dict: Dictionary with Language instances.

    Raises:
        FileExistsError: Raised if the database already exist.
        peewee.OperationalError: Raised if languages or DamageClass tables
            already exists or they objects already exist.

    """
    # Check if there is a preexisting database
    if os.path.isfile(path):
        msg = "The database '{}' already exist.".format(path)
        raise FileExistsError(msg)

    # Connection and creation and initialization of Language table
    models.db.init(path)
    models.db.connect()
    models.db.create_tables([models.Language, models.DamageClass], safe=True)

    # Create languages
    languages = {
        Lang.fr: models.Language.get_or_create(code="fr", name="Français")[0],
        Lang.en: models.Language.get_or_create(code="en", name="English")[0],
    }

    # Create damage class
    models.DamageClass.get_or_create(id=1, name="Status", image="status.png")
    models.DamageClass.get_or_create(
        id=2, name="Physical", image="physical.png"
    )
    models.DamageClass.get_or_create(id=3, name="Special", image="special.png")

    return models.db, languages


# =========================================================================== #
#                               Version builder                               #
# =========================================================================== #
def build_versions(pkm_db, languages, csv_dir):
    """Build the pokémon's version database with data from pokeapi's csv files.

    Args:
        pkm_db (pokedia.models.db): Pokediadb database.
        languages (dict): Dictionary of supported languages.
        csv_dir (str): Path to csv directory.

    """
    pkm_db.create_tables([models.Version, models.VersionTranslation])
    csv_dir = Path(csv_dir).absolute()

    # Extract data about versions from pokedia csv files
    pkm_versions = dbuilder.version.get_version_groups(
        csv_dir, dbuilder.version.get_versions(csv_dir)
    )
    pkm_version_names = dbuilder.version.get_version_names(
        csv_dir, pkm_versions, languages
    )

    # Insert all collected data about versions in the database
    with pkm_db.atomic():
        models.Version.insert_many(pkm_versions).execute()
        models.VersionTranslation.insert_many(pkm_version_names).execute()


# =========================================================================== #
#                                 Type builder                                #
# =========================================================================== #
def build_types(pkm_db, languages, csv_dir):
    """Build the pokémon's types database with data from pokeapi's csv files.

    Args:
        pkm_db (pokedia.models.db): Pokediadb database.
        languages (dict): Dictionary of supported languages.
        csv_dir (str): Path to csv directory.

    """
    pkm_db.create_tables([
        models.Type, models.TypeTranslation, models.TypeEfficacy
    ])
    csv_dir = Path(csv_dir).absolute()

    # Extract data about types from pokedia csv files
    pkm_types = dbuilder.type.get_types(csv_dir)
    pkm_type_eff = dbuilder.type.get_type_efficacies(csv_dir, pkm_types)
    pkm_type_names = dbuilder.type.get_type_names(
        csv_dir, pkm_types, languages
    )

    # Insert all collected data about types in the database
    with pkm_db.atomic():
        models.Type.insert_many(list(pkm_types.values())).execute()
        models.TypeEfficacy.insert_many(pkm_type_eff).execute()
        models.TypeTranslation.insert_many(pkm_type_names).execute()


# =========================================================================== #
#                               Ability builder                               #
# =========================================================================== #
def build_abilities(pkm_db, languages, csv_dir):
    """Build pokémon's abilities database with data from pokeapi's csv files.

    Args:
        pkm_db (pokedia.models.db): Pokediadb database.
        languages (dict): Dictionary of supported languages.
        csv_dir (str): Path to csv directory.

    """
    pkm_db.create_tables([models.Ability, models.AbilityTranslation])
    csv_dir = Path(csv_dir).absolute()

    # Extract data about abilities from pokedia csv files
    pkm_abilities = dbuilder.ability.get_abilities(csv_dir)
    pkm_ability_trans = dbuilder.ability.get_ability_names(
        csv_dir, pkm_abilities, languages
    )
    dbuilder.ability.update_ability_effects(
        csv_dir, pkm_ability_trans, languages
    )

    # Insert all collected data about abilities in the database
    with pkm_db.atomic():
        models.Ability.insert_many(list(pkm_abilities.values())).execute()

        data = list(pkm_ability_trans.values())
        size = get_max_size(data)
        for i in range(0, len(data), size):
            models.AbilityTranslation.insert_many(data[i:i+size]).execute()


# =========================================================================== #
#                                 Move builder                                #
# =========================================================================== #
def build_moves(pkm_db, languages, csv_dir):
    """Build the pokémon moves database with data from pokeapi's csv files.

    Args:
        pkm_db (pokedia.models.db): Pokediadb database.
        languages (dict): Dictionary of supported languages.
        csv_dir (str): Path to csv directory.

    """
    pkm_db.create_tables([models.Move, models.MoveTranslation])
    csv_dir = Path(csv_dir).absolute()

    # Extract data about moves from pokedia csv files
    pkm_moves = dbuilder.move.get_moves(csv_dir)
    pkm_move_trans = dbuilder.move.get_move_names(
        csv_dir, pkm_moves, languages
    )
    dbuilder.move.update_move_effects(csv_dir, pkm_move_trans, languages)

    # Insert all collected data about moves in the database
    with pkm_db.atomic():
        move_data = list(pkm_moves.values())
        size = get_max_size(move_data)
        for i in range(0, len(move_data), size):
            models.Move.insert_many(move_data[i:i+size]).execute()

        move_trans_data = list(pkm_move_trans.values())
        size = get_max_size(move_trans_data)
        for i in range(0, len(move_data), size):
            models.MoveTranslation.insert_many(
                move_trans_data[i:i+size]
            ).execute()


# =========================================================================== #
#                               Pokemon builder                               #
# =========================================================================== #
def build_pokemons(pkm_db, languages, csv_dir):
    """Build the pokémon abilities database with data from pokeapi's csv files.

    Args:
        pkm_db (pokedia.models.db): Pokediadb database.
        languages (dict): Dictionary of supported languages.
        csv_dir (str): Path to csv directory.

    Raises:
        peewee.OperationalError: Raised if ability tables haven't been build.

    """
    pkm_db.create_tables([
        models.Pokemon, models.PokemonTranslation, models.PokemonAbility
    ])
    csv_dir = Path(csv_dir).absolute()

    # Extract data about pokémons from pokedia csv files
    pkms = dbuilder.pokemon.get_pokemons(csv_dir)
    pkm_abilities = dbuilder.pokemon.get_pokemon_abilities(csv_dir, pkms)
    pkm_trans = dbuilder.pokemon.get_pokemon_trans(csv_dir, pkms, languages)

    # Insert all collected data about pokémons in the database
    with pkm_db.atomic():
        pkm_data = list(pkms.values())
        size = get_max_size(pkm_data)
        for i in range(0, len(pkm_data), size):
            models.Pokemon.insert_many(pkm_data[i:i+size]).execute()

        size = get_max_size(pkm_abilities)
        for i in range(0, len(pkm_abilities), size):
            models.PokemonAbility.insert_many(
                pkm_abilities[i:i+size]
            ).execute()

        size = get_max_size(pkm_trans)
        for i in range(0, len(pkm_trans), size):
            models.PokemonTranslation.insert_many(
                pkm_trans[i:i+size]
            ).execute()
