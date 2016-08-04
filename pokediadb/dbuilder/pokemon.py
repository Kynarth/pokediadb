import csv

from pokediadb import models


def get_pokemons(csv_dir):
    """Get information to build pokediadb.models.Pokemon objects.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.

    Returns:
        dict: Dict of dict containing infos to build
            pokediadb.models.Pokemon object.

    Raises:
        FileNotFoundError: Raised if pokemon.csv does not exist.

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
        FileNotFoundError: Raised if pokemon_abilities.csv does not exist.

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

    Raises:
        FileNotFoundError: Raised if pokemon_species_names.csv does not exist.

    """
    pkm_trans = []
    with (csv_dir / "pokemon_species_names.csv").open() as f_pkm_trans:
        reader = csv.reader(f_pkm_trans)
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
