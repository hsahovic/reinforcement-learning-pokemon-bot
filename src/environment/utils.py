import json
import numpy as np

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

def data_flattener(data) -> list:
    if data is None:
        return [0]
    elif isinstance(data, int):
        return [float(data)]
    elif isinstance(data, float):
        return [data]
    elif isinstance(data, bool):
        return [float(data)]
    elif isinstance(data, dict):
        to_return = []
        for key in sorted(data.keys()):
            to_return += data_flattener(data[key])
        return to_return
    elif isinstance(data, list):
        to_return = []
        for el in data:
            to_return += data_flattener(el)
        return to_return
    elif isinstance(data, tuple):
        to_return = []
        for el in data:
            to_return += data_flattener(el)
        return to_return
    else:
        raise ValueError(f'Type {type(data)} (with value {data}) is not compatible with function data_flattener')
