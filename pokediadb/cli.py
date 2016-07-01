"""
Pokediadb is a simple command line interface to generate a pokémon sqlite
database from csv and sprites contained in the pokeapi repository.
See: https://github.com/PokeAPI/pokeapi
"""

import click


@click.command()
@click.argument('name', default='world', required=False)
def main(name):
    """
    CLI tool to generate a sqlite database with data from pokeapi repository.
    """
    click.echo('Hello, {}.'.format(name))
