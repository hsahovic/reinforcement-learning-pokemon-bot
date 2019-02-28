import json

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
