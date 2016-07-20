"""Contains all project's enums."""

from enum import IntEnum
from enum import Enum


class Lang(IntEnum):
    """Enumeration of the different supported language.

    Each number corresponds to the language id in the pokeapi database.

    """
    fr = 5
    en = 9


class Log(Enum):
    """Enumeration of the different kind of log message."""
    INFO = "[INFO]: "
    WARNING = "[WARNING]: "
    ERROR = "[ERROR]: "
