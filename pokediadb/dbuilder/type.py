import csv


def get_types(csv_dir):
    """Get information to build pokediadb.models.Type objects.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.

    Returns:
        dict: Dict of dict containing infos to build
            pokediadb.models.Type object.

    Raises:
        FileNotFoundError: Raised if types.csv does not exist.

    """
    pkm_types = {}
    with (csv_dir / "types.csv").open(encoding="utf8") as f_type:
        reader = csv.reader(f_type)
        next(reader)  # Skip header

        for row in reader:
            type_id = int(row[0])

            # Skip shadow and unknown types
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

    Raises:
        FileNotFoundError: Raised if type_efficacy.csv does not exist.

    """
    pkm_type_eff = []
    with (csv_dir / "type_efficacy.csv").open(encoding="utf8") as f_type_eff:
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

    Raises:
        FileNotFoundError: Raised if type_names.csv does not exist.

    """
    pkm_type_names = []
    with (csv_dir / "type_names.csv").open(encoding="utf8") as f_type_name:
        reader = csv.reader(f_type_name)
        next(reader)  # Skip header

        for row in reader:
            type_id = int(row[0])
            lang_id = int(row[1])

            # Skip shadow and unknown types
            if type_id > 10000:
                break

            if lang_id in languages:
                pkm_type_names.append({
                    "type": pkm_types[type_id]["id"],
                    "lang": languages[lang_id],
                    "name": row[2]
                })

    return pkm_type_names
