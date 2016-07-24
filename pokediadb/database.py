"""Helper functions with database."""

import os
import csv
from pathlib import Path

from pokediadb import models
from pokediadb.models import db
from pokediadb.enums import Lang
from pokediadb.models import Language


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
    # Check if there is a prexisting database
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

    # Collect pokémon type generations
    pkm_types = []
    with (csv_dir / "types.csv").open() as f_type:
        reader = csv.reader(f_type)
        next(reader)  # Skip header

        for row in reader:
            # Skip weird types
            if int(row[0]) > 10000:
                break

            pkm_types.append({"id": int(row[0]), "generation": int(row[2])})

    # Collect pokémon type efficacy
    pkm_type_eff = []
    with (csv_dir / "type_efficacy.csv").open() as f_type_eff:
        reader = csv.reader(f_type_eff)
        next(reader)  # Skip header

        for row in reader:
            pkm_type_eff.append({
                "damage_type": pkm_types[int(row[0]) - 1]["id"],
                "target_type": pkm_types[int(row[1]) - 1]["id"],
                "damage_factor": int(row[2])
            })

    # Collect pokémon type names in different languages
    pkm_type_names = []
    with (csv_dir / "type_names.csv").open() as f_type_name:
        reader = csv.reader(f_type_name)
        next(reader)  # Skip header

        for row in reader:
            # Skip weird types
            type_id = int(row[0])
            if type_id > 10000:
                break

            lang_id = int(row[1])
            if lang_id in languages:
                pkm_type_names.append({
                    "type": pkm_types[type_id - 1]["id"],
                    "lang": languages[int(row[1])],
                    "name": row[2]
                })

    # Insert all collected data in the database
    with pkm_db.atomic():
        models.Type.insert_many(pkm_types).execute()
        models.TypeEfficacy.insert_many(pkm_type_eff).execute()
        models.TypeTranslation.insert_many(pkm_type_names).execute()


def build_abilities(pkm_db, languages, csv_dir):
    """Build pokémon's abilites database with data from pokeapi's csv files.

    Args:
        pkm_db (pokedia.models.db): Pokediadb database.
        languages (dict): Dictionary of supported languages.
        csv_dir (str): Path to csv directory.

    """
    pkm_db.create_tables([models.Ability, models.AbilityTranslation])
    csv_dir = Path(csv_dir).absolute()

    # Collect pokémon ability generations
    pkm_abilities = []
    with (csv_dir / "abilities.csv").open() as f_ability:
        reader = csv.reader(f_ability)
        next(reader)  # Skip header

        for row in reader:
            # Skip weird abilities
            if int(row[0]) > 10000:
                break

            pkm_abilities.append({
                "id": int(row[0]), "generation": int(row[2])
            })

    # Collect pokémon ability names in different languages
    pkm_ability_trans = {}  # Contains all fields needing translations
    with (csv_dir / "ability_names.csv").open() as f_ab_name:
        reader = csv.reader(f_ab_name)
        next(reader)  # Skip header

        for row in reader:
            # Skip weird types
            if int(row[0]) > 10000:
                break

            # Key for pkm_abilities_trans dictionary
            data_id = "{}-{}".format(row[0], row[1])
            if int(row[1]) in languages:
                pkm_ability_trans[data_id] = {
                    "ability": pkm_abilities[int(row[0]) - 1]["id"],
                    "lang": languages[int(row[1])],
                    "name": row[2]
                }

    # Collect pokémon ability effect in different languages
    with (csv_dir / "ability_flavor_text.csv").open() as f_ab_eff:
        reader = csv.reader(f_ab_eff)
        next(reader)  # Skip header

        for row in reader:
            # Skip older version since they are not complete
            if int(row[1]) != 16:
                continue

            lang_id = int(row[2])
            data_id = "{}-{}".format(row[0], row[2])
            effect = row[3].replace("\n", " ")
            if lang_id in languages:
                pkm_ability_trans[data_id]["effect"] = effect

    # Insert all collected data in the database
    with pkm_db.atomic():
        data = list(pkm_ability_trans.values())
        models.Ability.insert_many(pkm_abilities).execute()
        for i in range(0, len(data), SQL_MAX_VARIABLE_NUMBER):
            models.AbilityTranslation.insert_many(
                data[i:i+SQL_MAX_VARIABLE_NUMBER]
            ).execute()
