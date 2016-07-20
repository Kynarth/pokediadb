"""Helper functions with database."""

import os
import csv
from pathlib import Path

from pokediadb.models import db
from pokediadb.enums import Lang
from pokediadb.models import Language
from pokediadb.models import Type, TypeTranslation, TypeEfficacy


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
    pkm_db.create_tables([Type, TypeTranslation, TypeEfficacy])
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
    with (csv_dir / "type_efficacy.csv").open() as f_type_efficacy:
        reader = csv.reader(f_type_efficacy)
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
                    "type_id": pkm_types[type_id - 1]["id"],
                    "lang_id": languages[int(row[1])],
                    "name": row[2]
                })

    # Insert all collected data in the database
    with pkm_db.atomic():
        Type.insert_many(pkm_types).execute()
        TypeEfficacy.insert_many(pkm_type_eff).execute()
        TypeTranslation.insert_many(pkm_type_names).execute()
