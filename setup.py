"""
CLI tool to generate a sqlite database with data from pokeapi repository.
"""
import subprocess
from setuptools import find_packages, setup, Command


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
        print("Cleaning build, dist and egg-info directories.")
        subprocess.call(
            ['rm', '-r', 'build', 'dist', 'pokediadb.egg-info']
        )
        print("Cleaning done !")

dependencies = ['click']

setup(
    name='pokediadb',
    version='0.1.0',
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
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'pokediadb = pokediadb.cli:main',
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
    }
)
