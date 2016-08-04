import csv


def get_abilities(csv_dir):
    """Get information to build pokediadb.models.Ability objects.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.

    Returns:
        dict: Dict of dict containing infos to build
            pokediadb.models.Ability object.

    Raises:
        FileNotFoundError: Raised if abilities.csv does not exist.

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

    Raises:
        FileNotFoundError: Raised if ability_names.csv does not exist.

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

    Raises:
        FileNotFoundError:: Raised if ability_flavor_text.csv does not exist.

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
