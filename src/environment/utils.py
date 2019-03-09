# -*- coding: utf-8 -*-
"""
Utility functions and variables.

This file is part of the pokemon showdown reinforcement learning bot project,
created by Randy Kotti, Ombeline Lagé and Haris Sahovic as part of their
advanced topics in artifical intelligence course at Ecole Polytechnique.
"""

import json
import numpy as np

from typing import Generator

CATEGORIES = ["Physical", "Special", "Status"]
"""List of str: move categories"""

CONFIG_PATH = "config.json"
"""str: path to the config file"""

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)
    """dict: configuration dictionnary"""

TARGETS = [
    "any",
    "all",
    "randomNormal",
    "allAdjacent",
    "allyTeam",
    "normal",
    "self",
    "allAdjacentFoes",
    "allySide",
    "foeSide",
    "scripted",
]
"""List of str: possible target values for a move"""

TYPES = [
    "bug",
    "dark",
    "dragon",
    "electric",
    "fairy",
    "fighting",
    "fire",
    "flying",
    "ghost",
    "grass",
    "ground",
    "ice",
    "normal",
    "poison",
    "psychic",
    "rock",
    "steel",
    "water",
]
"""List of str: possible values for types"""

# TODO : add type chart

SECONDARIES = ["par", "brn", "frz", "psn", "slp", "flinch", "confusion"]
"""List of str: secondary effects a move can have"""

SEXES = ["F", "M", "N"]
"""List of str: possible values for pokemon sexes"""

with open("data/moves.json") as f:
    # These are magic regexes to convert from the .js moves file to working json, when
    # combined with some auto-formatting
    # ^    "((on.*)|(.*Callback))": function\(.*?\) {\n(.*\n)*?    },\n
    # ^      "((on.*)|(.*Callback))": function\(.*?\) {\n(.*\n)*?      },?\n
    # ^        "((on.*)|(.*Callback))": function\(.*?\) {\n(.*\n)*?        },?\n
    # //.*

    MOVES = json.load(f)
    """dict: move information, imported from Pokemon Showdown"""

with open("data/pokedex.json") as f:
    POKEDEX = json.load(f)


def _data_yielder(data) -> Generator:
    """
    Generator yielding data in a deterministric way from an arbitrary nested data 
    container.

    Args:
        data (arbitrary): The data source.

    Yields:
        float: The next value in the data source.

    Examples:
        >>> data = {'a' : [1, 2, 3], 'b' : 4, 'd' : False}
        >>> print([el for el in _data_yielder(data)])
        [1.0, 2.0, 3.0, 4.0, 0.0]

    """
    if isinstance(data, int):
        yield data
    elif isinstance(data, bool):
        yield 1 if data else 0
    elif data is None:
        yield 0
    elif isinstance(data, float):
        yield data
    elif isinstance(data, dict):
        for key in sorted(data.keys()):
            for el in _data_yielder(data[key]):
                yield el
    elif isinstance(data, list):
        for el in data:
            for foo in _data_yielder(el):
                yield foo
    elif isinstance(data, tuple):
        for el in data:
            for foo in _data_yielder(el):
                yield foo
    else:
        raise ValueError(
            f"Type {type(data)} (with value {data}) is not compatible with function data_flattener"
        )


def data_flattener(data) -> list:
    """
    Returns a flattened list of values extracted from an arbitrary nested data
    container in a determinisstic way.

    Args:
        data (arbitrary): The data source.

    Returns:
        float: The flattened array with values from the data source.

    Examples:
        >>> data = {'a' : [1, 2, 3], 'b' : 4, 'd' : False}
        >>> data_flattener(data)
        [1.0, 2.0, 3.0, 4.0, 0.0]

    """
    return [el for el in _data_yielder(data)]
