import csv


def get_versions(csv_dir):
    """Get version of pokemon's games.

    Args:
        csv_dir (pathlib.Path): Path to csv directory.

    Returns:
        list: List of dict containing infos to build
            pokediadb.models.Version object.

    Raises:
        FileNotFoundError: Raised if versions.csv does not exist.

    """
    pkm_versions = []
    with (csv_dir / "versions.csv").open(encoding="utf8") as f_version:
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

    Raises:
        FileNotFoundError: Raised if version_groups.csv does not exist.

    """
    with (csv_dir / "version_groups.csv").open(encoding="utf8") as f_v_group:
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

    Raises:
        FileNotFoundError: Raised if version_names.csv does not exist.

    """
    with (csv_dir / "version_names.csv").open(encoding="utf8") as f_v_name:
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
