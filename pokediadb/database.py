"""Helper functions with database."""

import os
from pathlib import Path

from pokediadb import models
from pokediadb.models import db
from pokediadb.enums import Lang
from pokediadb.models import Language
from pokediadb import dbuilder


SQL_MAX_VARIABLE_NUMBER = 200


def db_init(path):
    """Initialize pokémon database with the given name.

    Args:
        path (str): Path the sqlite database file.

    Returns:
        peewee.SqliteDatabase : Database instance.
        dict: Dictionary with Language instances.

    Raises:
        FileExistsError: Raised if the path argument indicates an existing
            file.

    """
    # Check if there is a preexisting database
    if os.path.isfile(path):
        raise FileExistsError("The file '{}' already exists.".format(path))

    # Connection and creation and initialization of Language table
    db.init(path)
    db.connect()
    db.create_table(Language)
    languages = {
        Lang.fr: Language.create(code="fr", name="Français"),
        Lang.en: Language.create(code="en", name="English"),
    }

    return db, languages


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
        data = list(pkm_ability_trans.values())
        models.Ability.insert_many(list(pkm_abilities.values())).execute()
        for i in range(0, len(data), SQL_MAX_VARIABLE_NUMBER):
            models.AbilityTranslation.insert_many(
                data[i:i+SQL_MAX_VARIABLE_NUMBER]
            ).execute()


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
        models.Move.insert_many(list(pkm_moves.values())).execute()
        models.MoveTranslation.insert_many(
            list(pkm_move_trans.values())
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
        models.Pokemon.insert_many(list(pkms.values())).execute()
        models.PokemonAbility.insert_many(pkm_abilities).execute()
        models.PokemonTranslation.insert_many(pkm_trans).execute()
