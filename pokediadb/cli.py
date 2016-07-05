"""
Pokediadb is a simple command line interface to generate a pokémon sqlite
database from csv and sprites contained in the pokeapi repository.
See: https://github.com/PokeAPI/pokeapi
"""

import sys
import shutil
import subprocess
from pathlib import Path

import click


@click.group()
def pokediadb():
    pass


@pokediadb.command(short_help="Download csv and sprites folders")
@click.argument("path", type=click.Path(exists=1, file_okay=0, writable=1),
                default=".")
def download(path):
    """Download the csv and sprites folders from pokeapi repository.

    They contains needed data to build the sqlite pokémon database.

    """
    # Create a pokeapi directory to clone the repository into
    try:
        pokeapi_dir = (Path(path).absolute() / "pokeapi")
        pokeapi_dir.mkdir()
    except FileExistsError:
        print(
            "A pokeapi folder already exists in {}".format(path),
            file=sys.stderr
        )
        raise click.Abort()

    # Clone pokeapi repository
    subprocess.run([
        "git", "clone", "https://github.com/PokeAPI/pokeapi.git",
        str(pokeapi_dir)
    ])

    # Extract csv and sprites folders in the given path directory and remove
    # pokeapi repository
    csv = pokeapi_dir / "data/v2/csv"
    sprites = pokeapi_dir / "data/v2/sprites"

    try:
        shutil.move(str(csv), str(pokeapi_dir.parent))
        shutil.move(str(sprites), str(pokeapi_dir.parent))
    except FileNotFoundError as e:  # pragma: no cover
        if csv.exists():
            shutil.rmtree(str(csv))

        if sprites.exists():
            shutil.rmtree(str(sprites))

        print(e, file=sys.stderr)
        shutil.rmtree(str(pokeapi_dir))
        raise click.Abort()
    finally:
        shutil.rmtree(str(pokeapi_dir))
