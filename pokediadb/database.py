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
def get_versions(csv_dir):
    """Get version of pokemon's games.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.

    Returns:
        list: List of dict containing infos to build
            pokediadb.models.Version object.

    """
    pkm_versions = []
    with (csv_dir / "versions.csv").open() as f_version:
        reader = csv.reader(f_version)
        next(reader)  # Skip header

        for row in reader:
            pkm_versions.append({"id": int(row[0]), "group": int(row[1])})

    return pkm_versions


def get_version_groups(csv_dir, pkm_versions):
    """Get the groups that classify games versions.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.
        pkm_versions (list): List of dict containing infos to build
            pokediadb.models.Versionobject.

    Returns
        list: Returns the list of versions with generation information.

    """
    with (csv_dir / "version_groups.csv").open() as f_v_group:
        reader = csv.reader(f_v_group)
        next(reader)  # Skip header

        for row in reader:
            for version in pkm_versions:
                if version.get("group", None) == int(row[0]):
                    version["generation"] = int(row[2])
                    del version["group"]

    return pkm_versions


def get_version_names(csv_dir, pkm_versions, languages):
    """Get the name of each game versions in different languages.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.
        pkm_versions (list): List of dict containing infos to build
            pokediadb.models.Version object.
        languages (dict): Dictionary of supported languages.

    Returns:
        list: List of dict containing infos to build
            pokediadb.models.VersionTranslation object.

    """
    with (csv_dir / "version_names.csv").open() as f_v_name:
        reader = csv.reader(f_v_name)
        next(reader)  # Skip header

        pkm_version_names = []
        for row in reader:
            version_id = int(row[0])
            lang_id = int(row[1])

            if lang_id in languages:
                version = [v for v in pkm_versions if v["id"] == version_id][0]
                pkm_version_names.append({
                    "version": version["id"], "lang": languages[lang_id],
                    "name": row[2]
                })

        return pkm_version_names


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
    pkm_versions = get_version_groups(csv_dir, get_versions(csv_dir))
    pkm_version_names = get_version_names(csv_dir, pkm_versions, languages)

    # Insert all collected data about versions in the database
    with pkm_db.atomic():
        models.Version.insert_many(pkm_versions).execute()
        models.VersionTranslation.insert_many(pkm_version_names).execute()


# =========================================================================== #
#                                 Type builder                                #
# =========================================================================== #
def get_types(csv_dir):
    """Get information to build pokediadb.models.Type objects.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.

    Returns:
        dict: Dict of dict containing infos to build
            pokediadb.models.Type object.

    """
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

    return pkm_types


def get_type_efficacies(csv_dir, pkm_types):
    """Get information to build pokediadb.models.TypeEfficacy objects.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.
        pkm_types (dict): Dict of dict containing type infos.

    Returns:
        list: Dict containing infos to build
            pokediadb.models.TypeEfficacy object.

    """
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

    return pkm_type_eff


def get_type_names(csv_dir, pkm_types, languages):
    """Get the name of each pokémon type in different languages.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.
        pkm_types (dict): Dict of dict containing type infos.
        languages (dict): Dictionary of supported languages.

    Returns:
        list: Dict containing infos to build
            pokediadb.models.TypeTranslation object.

    """
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

    return pkm_type_names


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
    pkm_types = get_types(csv_dir)
    pkm_type_eff = get_type_efficacies(csv_dir, pkm_types)
    pkm_type_names = get_type_names(csv_dir, pkm_types, languages)

    # Insert all collected data about types in the database
    with pkm_db.atomic():
        models.Type.insert_many(list(pkm_types.values())).execute()
        models.TypeEfficacy.insert_many(pkm_type_eff).execute()
        models.TypeTranslation.insert_many(pkm_type_names).execute()


# =========================================================================== #
#                               Ability builder                               #
# =========================================================================== #
def get_abilities(csv_dir):
    """Get information to build pokediadb.models.Ability objects.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.

    Returns:
        dict: Dict of dict containing infos to build
            pokediadb.models.Ability object.

    """
    pkm_abilities = {}
    with (csv_dir / "abilities.csv").open() as f_ability:
        reader = csv.reader(f_ability)
        next(reader)  # Skip header

        for row in reader:
            ability_id = int(row[0])
            # Skip weird abilities
            if ability_id > 10000:
                break

            pkm_abilities[ability_id] = {
                "id": int(row[0]), "generation": int(row[2])
            }

    return pkm_abilities


def get_ability_names(csv_dir, pkm_abilities, languages):
    """Get the name of each pokémon ability in different languages.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.
        pkm_abilities (dict): Dict of dict containing ability infos.
        languages (dict): Dictionary of supported languages.

    Returns:
        list: Dict containing infos to build
            pokediadb.models.AbilityTranslation object.

    """
    pkm_ability_trans = {}  # Contains all fields needing translations
    with (csv_dir / "ability_names.csv").open() as f_ab_name:
        reader = csv.reader(f_ab_name)
        next(reader)  # Skip header

        for row in reader:
            ability_id = int(row[0])
            lang_id = int(row[1])

            # Skip weird types
            if ability_id > 10000:
                break

            # Key for pkm_abilities_trans dictionary
            data_id = "{}-{}".format(ability_id, lang_id)
            if lang_id in languages:
                pkm_ability_trans[data_id] = {
                    "ability": pkm_abilities[ability_id]["id"],
                    "lang": languages[lang_id],
                    "name": row[2]
                }

        return pkm_ability_trans


def update_ability_effects(csv_dir, pkm_ability_trans, languages):
    """Update the dict of AbilityTranslation infos to add effect text.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.
        pkm_ability_trans (dict): Dict of dict containing
            infos about ability that need translations.
        languages (dict): Dictionary of supported languages.

    """
    with (csv_dir / "ability_flavor_text.csv").open() as f_ab_eff:
        reader = csv.reader(f_ab_eff)
        next(reader)  # Skip header

        for row in reader:
            # Skip older version since they are not complete
            if int(row[1]) != 16:
                continue

            lang_id = int(row[2])
            data_id = "{}-{}".format(row[0], lang_id)
            effect = row[3].replace("\n", " ")
            if lang_id in languages:
                pkm_ability_trans[data_id]["effect"] = effect


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
    pkm_abilities = get_abilities(csv_dir)
    pkm_ability_trans = get_ability_names(csv_dir, pkm_abilities, languages)
    update_ability_effects(csv_dir, pkm_ability_trans, languages)

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
def get_moves(csv_dir):
    """Get information to build pokediadb.models.Move objects.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.

    Returns:
        dict: Dict of dict containing infos to build
            pokediadb.models.Move object.

    Raises:
        peewee.OperationalError: Raised if type tables haven't been build.

    """
    pkm_moves = {}
    with (csv_dir / "moves.csv").open() as f_move:
        reader = csv.reader(f_move)
        next(reader)  # Skip header

        for row in reader:
            move_id = int(row[0])

            # Skip weird moves
            if move_id > 10000:
                break

            pkm_moves[move_id] = {
                "id": move_id, "generation": int(row[2]),
                "type": models.Type.get(
                    models.Type.id == int(row[3])
                ),
                "power": int(row[4]), "pp": int(row[5]),
                "accuracy": int(row[6]), "priority": int(row[7]),
                "damage_class": row[9]
            }

    return pkm_moves


def get_move_names(csv_dir, pkm_moves, languages):
    """Get the name of each pokémon move in different languages.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.
        pkm_moves (dict): Dict of dict containing move infos.
        languages (dict): Dictionary of supported languages.

    Returns:
        list: Dict containing infos to build
            pokediadb.models.MoveTranslation object.

    """
    pkm_move_trans = {}
    with (csv_dir / "move_names.csv").open() as f_move_name:
        reader = csv.reader(f_move_name)
        next(reader)  # Skip header

        for row in reader:
            move_id = int(row[0])
            lang_id = int(row[1])

            # Skip weird moves
            if move_id > 10000:
                break

            if lang_id in languages:
                data_id = "{}-{}".format(move_id, lang_id)
                pkm_move_trans[data_id] = {
                    "move": pkm_moves[move_id]["id"],
                    "lang": languages[lang_id], "name": row[2]
                }

    return pkm_move_trans


def update_move_effects(csv_dir, pkm_move_trans, languages):
    """Update the dict of MoveTranslation infos to add effect text.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.
        pkm_move_trans (dict): Dict of dict containing
            infos about move that need translations.
        languages (dict): Dictionary of supported languages.

    """
    with (csv_dir / "move_flavor_text.csv").open() as f_move_eff:
        reader = csv.reader(f_move_eff)
        next(reader)  # Skip header

        for row in reader:
            if row[1] == "16" and int(row[2]) in languages:
                data_id = "{}-{}".format(row[0], row[2])
                pkm_move_trans[data_id]["effect"] = row[3]


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
    pkm_moves = get_moves(csv_dir)
    pkm_move_trans = get_move_names(csv_dir, pkm_moves, languages)
    update_move_effects(csv_dir, pkm_move_trans, languages)

    # Insert all collected data about moves in the database
    with pkm_db.atomic():
        models.Move.insert_many(list(pkm_moves.values())).execute()
        models.MoveTranslation.insert_many(
            list(pkm_move_trans.values())
        ).execute()


# =========================================================================== #
#                               Pokemon builder                               #
# =========================================================================== #
def get_pokemons(csv_dir):
    """Get information to build pokediadb.models.Pokemon objects.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.

    Returns:
        dict: Dict of dict containing infos to build
            pokediadb.models.Pokemon object.

    """
    pkms = {}
    with (csv_dir / "pokemon.csv").open() as f_pkm:
        reader = csv.reader(f_pkm)
        next(reader)  # Skip header

        for row in reader:
            pkm_id = int(row[0])

            # Skip mega evolution and weird pokémons
            if pkm_id > 10000:
                break

            pkms[pkm_id] = {
                "id": pkm_id, "national_id": int(row[2]),
                "height": float(row[3]) / 10, "weight": float(row[4]) / 10,
                "base_xp": int(row[5])
            }

    return pkms


def get_pokemon_abilities(csv_dir, pkms):
    """Get information to build pokediadb.models.PokemonAbility objects.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.

    Returns:
        dict: Dict of dict containing infos to build
            pokediadb.models.PokemonAbility object.

    Raises:
        peewee.OperationalError: Raised if ability tables haven't been build.

    """
    pkm_abilities = []
    with (csv_dir / "pokemon_abilities.csv").open() as f_pkm_ab:
        reader = csv.reader(f_pkm_ab)
        next(reader)  # Skip header

        for row in reader:
            pkm_id = int(row[0])

            # Skip mega evolution and weird pokémons
            if pkm_id > 10000:
                break

            pkm_abilities.append({
                "pokemon": pkms[pkm_id]["id"],
                "ability": models.Ability.get(
                    models.Ability.id == int(row[1])
                ),
                "hidden": int(row[2]), "slot": int(row[3])
            })

    return pkm_abilities


def get_pokemon_trans(csv_dir, pkms, languages):
    """Get information to build pokediadb.models.PokemonTranslation objects.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.
        pkms (dict): Dict of dict containing pokémons infos.
        languages (dict): Dictionary of supported languages.

    Returns:
        list: Dict containing infos to build
            pokediadb.models.PokmeonTranslation object.

    """
    pkm_trans = []
    with (csv_dir / "pokemon_species_names.csv").open() as f_pkm_ab:
        reader = csv.reader(f_pkm_ab)
        next(reader)  # Skip header

        for row in reader:
            lang_id = int(row[1])

            if lang_id in languages:
                pkm_trans.append({
                    "pokemon": pkms[int(row[0])]["id"],
                    "lang": languages[lang_id],
                    "name": row[2], "genus": row[3]
                })

    return pkm_trans


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
    pkms = get_pokemons(csv_dir)
    pkm_abilities = get_pokemon_abilities(csv_dir, pkms)
    pkm_trans = get_pokemon_trans(csv_dir, pkms, languages)

    # Insert all collected data about pokémons in the database
    with pkm_db.atomic():
        models.Pokemon.insert_many(list(pkms.values())).execute()
        models.PokemonAbility.insert_many(pkm_abilities).execute()
        models.PokemonTranslation.insert_many(pkm_trans).execute()
