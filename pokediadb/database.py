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
    pkm_types = {}
    with (csv_dir / "types.csv").open() as f_type:
        reader = csv.reader(f_type)
        next(reader)  # Skip header

        for row in reader:
            # Skip weird types
            type_id = int(row[0])
            if type_id > 10000:
                break

            pkm_types[type_id] = {"id": type_id, "generation": int(row[2])}

    # Collect pokémon type efficacy
    pkm_type_eff = []
    with (csv_dir / "type_efficacy.csv").open() as f_type_eff:
        reader = csv.reader(f_type_eff)
        next(reader)  # Skip header

        for row in reader:
            pkm_type_eff.append({
                "damage_type": pkm_types[int(row[0])]["id"],
                "target_type": pkm_types[int(row[1])]["id"],
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
                    "type": pkm_types[type_id]["id"],
                    "lang": languages[lang_id],
                    "name": row[2]
                })

    # Insert all collected data in the database
    with pkm_db.atomic():
        models.Type.insert_many(list(pkm_types.values())).execute()
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
    pkm_abilities = {}
    with (csv_dir / "abilities.csv").open() as f_ability:
        reader = csv.reader(f_ability)
        next(reader)  # Skip header

        for row in reader:
            # Skip weird abilities
            if int(row[0]) > 10000:
                break

            pkm_abilities[int(row[0])] = {
                "id": int(row[0]), "generation": int(row[2])
            }

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
                    "ability": pkm_abilities[int(row[0])]["id"],
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
        models.Ability.insert_many(list(pkm_abilities.values())).execute()
        for i in range(0, len(data), SQL_MAX_VARIABLE_NUMBER):
            models.AbilityTranslation.insert_many(
                data[i:i+SQL_MAX_VARIABLE_NUMBER]
            ).execute()


def build_pokemons(pkm_db, languages, csv_dir):
    """Build the pokémon abilities database with data from pokeapi's csv files.

    Args:
        pkm_db (pokedia.models.db): Pokediadb database.
        languages (dict): Dictionary of supported languages.
        csv_dir (str): Path to csv directory.

    Raises:
        peewee.OperationalError: Raised if abilities tables haven't been build.

    """
    pkm_db.create_tables([
        models.Pokemon, models.PokemonTranslation, models.PokemonAbility
    ])
    csv_dir = Path(csv_dir).absolute()

    # Collect general pokemon data
    pkms = {}
    with (csv_dir / "pokemon.csv").open() as f_pkm:
        reader = csv.reader(f_pkm)
        next(reader)  # Skip header

        for row in reader:
            # Skip mega evolution and weird pokemons
            if int(row[0]) > 10000:
                break

            pkms[int(row[0])] = {
                "id": int(row[0]), "national_id": int(row[2]),
                "height": int(row[3]), "weight": int(row[4]),
                "base_xp": int(row[5])
            }

    # Search abilities for each pokémon
    pkm_abilities = []
    with (csv_dir / "pokemon_abilities.csv").open() as f_pkm_ab:
        reader = csv.reader(f_pkm_ab)
        next(reader)  # Skip header

        for row in reader:
            # Skip mega evolution and weird pokemons
            if int(row[0]) > 10000:
                break

            pkm_abilities.append({
                "pokemon": pkms[int(row[0])]["id"],
                "ability": models.Ability.get(
                    models.Ability.id == int(row[1])
                ),
                "hidden": int(row[2]), "slot": int(row[3])
            })

    # Search pokémon names and genus in different languages
    pkm_trans = []
    with (csv_dir / "pokemon_species_names.csv").open() as f_pkm_ab:
        reader = csv.reader(f_pkm_ab)
        next(reader)  # Skip header

        for row in reader:
            if int(row[1]) in languages:
                pkm_trans.append({
                    "pokemon": pkms[int(row[0])]["id"],
                    "lang": languages[int(row[1])],
                    "name": row[2], "genus": row[3]
                })

    # Insert all collected data in the database
    with pkm_db.atomic():
        models.Pokemon.insert_many(list(pkms.values())).execute()
        models.PokemonAbility.insert_many(pkm_abilities).execute()
        models.PokemonTranslation.insert_many(pkm_trans).execute()
