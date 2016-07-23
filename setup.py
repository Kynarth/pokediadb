"""
CLI tool to generate a sqlite database with data from pokeapi repository.
"""
import shutil
from setuptools import find_packages, setup, Command
from setuptools.command.install import install


def clean():
    print("Cleaning build, dist and egg-info directories.")
    try:
        shutil.rmtree("build")
    except FileNotFoundError:
        pass

    try:
        shutil.rmtree("dist")
    except FileNotFoundError:
        pass

    try:
        shutil.rmtree("pokediadb.egg-info")
    except FileNotFoundError:
        pass

    print("Cleaning done !")


class InstallCommand(install):
    """Custom install command that call clean command after installation."""
    description = (
        "Custom install command that call command clean after installation."
    )

    def run(self):
        install.run(self)
        clean()


class CleanCommand(Command):
    """Custom clean command to get remove build dist and egg-info folders."""
    user_options = []
    description = (
        "Custom clean command to get remove build dist and egg-info folders."
    )

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        clean()


DEPENDENCIES = ['click', 'colorama', 'peewee']

setup(
    name='pokediadb',
    version='0.2.0',
    url='https://github.com/kynarth/pokediadb',
    license='MIT',
    author='Kynarth Alseif',
    author_email='kynarth.alseif@gmail.com',
    description=(
        'CLI tool to generate a sqlite database with data from pokeapi '
        'repository.'
    ),
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=DEPENDENCIES,
    entry_points={
        'console_scripts': [
            'pokediadb = pokediadb.cli:pokediadb',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: MIT License",
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Windows',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities',
    ],
    cmdclass={
        'clean': CleanCommand,
        'install': InstallCommand,
    }
)
