import json

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
