import csv

from pokediadb import models


def get_moves(csv_dir):
    """Get information to build pokediadb.models.Move objects.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.

    Returns:
        dict: Dict of dict containing infos to build
            pokediadb.models.Move object.

    Raises:
        peewee.OperationalError: Raised if type tables haven't been build.
        FileNotFoundError:: Raised if moves.csv does not exist.

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

    Raises:
        FileNotFoundError:: Raised if move_names.csv does not exist.

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

    Raises:
        FileNotFoundError: Raised if move_flavor_text.csv does not exist.

    """
    with (csv_dir / "move_flavor_text.csv").open() as f_move_eff:
        reader = csv.reader(f_move_eff)
        next(reader)  # Skip header

        for row in reader:
            if row[1] == "16" and int(row[2]) in languages:
                data_id = "{}-{}".format(row[0], row[2])
                pkm_move_trans[data_id]["effect"] = row[3]
