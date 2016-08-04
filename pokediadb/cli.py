"""
Pokediadb is a simple command line interface to generate a pokémon sqlite
database from csv and sprites contained in the pokeapi repository.
See: https://github.com/PokeAPI/pokeapi
"""

import shutil
import subprocess
from pathlib import Path

import click

from pokediadb import log
from pokediadb import database as pdb


def validate_dbname(ctx, params, value):
    """Validate a database name."""
    # pylint: disable=W0613
    # Check for forbidden characters
    forbidden_chars = ["/", "<", ">", ":", "\"", "\\", "|", "?", "*"]
    if any([c in value for c in forbidden_chars]):
        raise click.BadParameter("Invalid file name.")

    # Check for multiple extensions
    if len(value.split(".")) > 2:
        raise click.BadParameter("Invalid file name.")

    # Check for no extension
    try:
        _, ext = value.split(".")
    except ValueError:
        ext = "sql"
        value += "." + ext

    # Check for wrong extension
    if ext not in ["sql", "sqlite3", "sqlite", "sqlite2", "db"]:
        raise click.BadParameter("Invalid file name extension")

    return value


@click.group()
def pokediadb():
    pass


@pokediadb.command(short_help="Download csv and sprites folders")
@click.argument("path", type=click.Path(exists=1, file_okay=0, writable=1),
                default=".")
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
def download(path, verbose):
    """Download the csv and sprites folders from pokeapi repository.

    They contains needed data to build the sqlite pokémon database.

    """
    # Create a pokeapi directory to clone the repository into
    path = Path(path).absolute()
    try:
        pokeapi_dir = path / "pokeapi"
        pokeapi_dir.mkdir()
    except FileExistsError:
        log.error("A pokeapi folder already exists in {}".format(path))
        raise click.Abort()

    # Check if there is no csv nor sprites folders in the given directory
    if (path / "csv").exists() or (path / "sprites").exists():
        log.error("Dir: {} contains a csv or sprites directory!".format(path))
        raise click.Abort()

    # Clone pokeapi repository
    log.info("Cloning pokeapi repository", verbose)
    subprocess.run([
        "git", "clone", "-q", "https://github.com/PokeAPI/pokeapi.git",
        str(pokeapi_dir)
    ])

    # Extract csv and sprites folders in the given path directory and remove
    # pokeapi repository
    log.info("Extracting csv and sprites folders.")
    csv = pokeapi_dir / "data/v2/csv"
    sprites = pokeapi_dir / "data/v2/sprites"

    try:
        shutil.move(str(csv), str(pokeapi_dir.parent))
        shutil.move(str(sprites), str(pokeapi_dir.parent))
    except FileNotFoundError as err:  # pragma: no cover
        log.error(err)
        if csv.exists():
            shutil.rmtree(str(csv))

        if sprites.exists():
            shutil.rmtree(str(sprites))

        shutil.rmtree(str(pokeapi_dir))
        raise click.Abort()
    finally:
        shutil.rmtree(str(pokeapi_dir))


@pokediadb.command(short_help="Generate PKM sqlite database.")
@click.argument("path", type=click.Path(exists=1, file_okay=0, writable=1),
                default=".")
@click.option("--name", "-n", type=str, default="pokediadb.sql",
              callback=validate_dbname)
@click.option("-v", "--verbose", is_flag=True, help="Explain the process")
@click.pass_context
def generate(ctx, path, name, verbose):
    dir_path = Path(path).absolute()
    file_path = dir_path / name
    csv_path = dir_path / "csv"

    # Database initialization
    log.info("Initializating {}".format(name), verbose)
    try:
        db, languages = pdb.db_init(str(file_path))
    except FileExistsError as err:
        log.error("{}".format(err))
        raise click.Abort()

    # Search for csv and sprites directories. If they are not in the provided
    # directory, they will be downloaded.
    if not csv_path.is_dir() or not (dir_path / "sprites").is_dir():
        ctx.invoke(download, path=path, verbose=verbose)

    log.info("Building versions tables...", verbose)
    pdb.build_versions(db, languages, csv_path)

    log.info("Building types tables...", verbose)
    pdb.build_types(db, languages, csv_path)

    log.info("Building abilities tables...", verbose)
    pdb.build_abilities(db, languages, csv_path)

    log.info("Building moves tables...", verbose)
    pdb.build_moves(db, languages, csv_path)

    log.info("Building pokemons tables...", verbose)
    pdb.build_pokemons(db, languages, csv_path)
