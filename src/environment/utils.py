import json
import numpy as np

from typing import Generator

CATEGORIES = ["Physical", "Special", "Status"]

CONFIG_PATH = "src/config.json"
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

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

SECONDARIES = ["par", "brn", "frz", "psn", "slp", "flinch", "confusion"]

SEXES = ["F", "M", "N"]

with open("data/moves.json") as f:
    # These are magic regexes to convert from the .js moves file to working json, when
    # combined with some auto-formatting
    # ^    "((on.*)|(.*Callback))": function\(.*?\) {\n(.*\n)*?    },\n
    # ^      "((on.*)|(.*Callback))": function\(.*?\) {\n(.*\n)*?      },?\n
    # ^        "((on.*)|(.*Callback))": function\(.*?\) {\n(.*\n)*?        },?\n
    # //.*
    MOVES = json.load(f)

with open("data/pokedex.json") as f:
    POKEDEX = json.load(f)

def data_yielder(data) -> Generator:
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
            for el in data_yielder(data[key]):
                yield el
    elif isinstance(data, list):
        for el in data:
            for foo in data_yielder(el):
                yield foo
    elif isinstance(data, tuple):
        for el in data:
            for foo in data_yielder(el):
                yield foo
    else:
        raise ValueError(f'Type {type(data)} (with value {data}) is not compatible with function data_flattener')

def data_flattener(data) -> list:
    return [el for el in data_yielder(data)]
