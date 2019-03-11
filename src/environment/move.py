# -*- coding: utf-8 -*-
"""
Move class. Represents a move, usually associated with a pokemon.

This file is part of the pokemon showdown reinforcement learning bot project,
created by Randy Kotti, Ombeline Lagé and Haris Sahovic as part of their
advanced topics in artifical intelligence course at Ecole Polytechnique.

TODO:
- PP Management
- Flags management
- Hidden power type
- ZMove effects
"""
from environment.utils import CATEGORIES, MOVES, TARGETS, TYPES, SECONDARIES


empty_move = {
    "accuracy": 0,
    "auto_boosts": {
        "atk": (0, 0),
        "brn": (0, 0),
        "def": (0, 0),
        "frz": (0, 0),
        "par": (0, 0),
        "psn": (0, 0),
        "slp": (0, 0),
        "spa": (0, 0),
        "spd": (0, 0),
        "spe": (0, 0),
        "tox": (0, 0),
    },
    "base_power": 0,
    "boosts": {
        "atk": (0, 0),
        "brn": (0, 0),
        "def": (0, 0),
        "frz": (0, 0),
        "par": (0, 0),
        "psn": (0, 0),
        "slp": (0, 0),
        "spa": (0, 0),
        "spd": (0, 0),
        "spe": (0, 0),
        "tox": (0, 0),
    },
    "category": {category: False for category in CATEGORIES},
    "exists": 0,
    "max_pp": 0,
    "priority": 0,
    "secondaries": {
        "par": 0,
        "brn": 0,
        "frz": 0,
        "psn": 0,
        "slp": 0,
        "flinch": 0,
        "confusion": 0,
    },
    "target": {target: False for target in TARGETS},
    "type": {type_: False for type_ in TYPES},
    "z_boost": {
        "atk": 0,
        "spa": 0,
        "def": 0,
        "spd": 0,
        "spe": 0,
        "fnt": 0,
        "accuracy": 0,
        "evasion": 0,
    },
    "z_power": 0,
    "z_effect": False,
}
"""This dictionnary is used inplace of unknown moves"""

class Move:
    """
    Represents a move.
    """
    def __init__(self, move:str) -> None:
        """
        Move initialisation

        Args:
            move (str): the move name, that will be looked up in the move database
        """
        # Small name reformatting: we get rid of special characters
        move = "".join([char for char in move if char not in "-' "])

        # Hiddenpower is a special case
        if move.startswith("hiddenpower") and move[-1] in "0123456789":
            move = move[:-2]

        # Z-Move can sometimes be an issue
        if move not in MOVES and move.startswith("z"):
            raise ZMoveException

        self.name = move
        self.accuracy = (
            MOVES[move]["accuracy"]
            if not isinstance(MOVES[move]["accuracy"], bool)
            else 100
        )
        self.base_power = MOVES[move]["basePower"]
        self.category = MOVES[move]["category"]
        if self.category not in CATEGORIES:
            print("category", self.category)
        self.max_pp = MOVES[move]["pp"]
        self.priority = MOVES[move]["priority"]
        self.flags = MOVES[move]["flags"]

        # Boosts are stored as tuples; the first value corresponds to the boost degree (
        # +1, -3...) and the second to the corresponding probability
        self.boosts = {
            "tox": (0, 0),
            "psn": (0, 0),
            "slp": (0, 0),
            "par": (0, 0),
            "brn": (0, 0),
            "frz": (0, 0),
            "atk": (0, 0),
            "spa": (0, 0),
            "def": (0, 0),
            "spd": (0, 0),
            "spe": (0, 0),
        }
        self.auto_boosts = {
            "tox": (0, 0),
            "psn": (0, 0),
            "slp": (0, 0),
            "par": (0, 0),
            "brn": (0, 0),
            "frz": (0, 0),
            "atk": (0, 0),
            "spa": (0, 0),
            "def": (0, 0),
            "spd": (0, 0),
            "spe": (0, 0),
        }

        self.secondaries = {
            "par": 0,
            "brn": 0,
            "frz": 0,
            "psn": 0,
            "slp": 0,
            "flinch": 0,
            "confusion": 0,
        }
        if "secondary" in MOVES[move]:
            if MOVES[move]["secondary"]:
                self.add_secondary(MOVES[move]["secondary"])
        elif "secondaries" in MOVES[move]:
            for secondary in MOVES[move]["secondaries"]:
                self.add_secondary(secondary)

        self.target = MOVES[move]["target"]
        if self.target not in TARGETS:
            print("target", self.target)
        self.type = MOVES[move]["type"].lower()
        if self.type not in TYPES:
            print("type", self.type)

        self.z_boost = {
            "atk": 0,
            "spa": 0,
            "def": 0,
            "spd": 0,
            "spe": 0,
            "fnt": 0,
            "accuracy": 0,
            "evasion": 0,
        }
        if "zMoveBoost" in MOVES[move]:
            for key, val in MOVES[move]["zMoveBoost"].items():
                if key not in self.z_boost:
                    print("z boost", key)
                else:
                    self.z_boost[key] = val
        if "zMovePower" in MOVES[move]:
            self.z_power = MOVES[move]["zMovePower"]
        else:
            self.z_power = 0
        if "zMoveEffect" in MOVES[move]:
            self.z_effect = True
        else:
            self.z_effect = False

    def __repr__(self) -> str:
        """
        String representation of the Move, in the form "Move object: name"
        """
        return f"Move object: {self.name}"

    def add_secondary(self, effect:dict) -> None:
        """
        Add a secondary effect.

        Arg:
            effect (dict): dictionnary describing the effect, from the move database
        """
        if "boosts" in effect:
            for stat, val in effect["boosts"].items():
                if stat not in self.boosts:
                    print("stat in boost", stat)
                self.boosts[stat] = (val, effect["chance"])
        elif "status" in effect:
            if effect["status"] not in SECONDARIES:
                print("UNKNOWN SECONDARY", effect["status"])
            else:
                self.secondaries[effect["status"]] = effect["chance"]
        elif "volatileStatus" in effect:
            if effect["volatileStatus"] not in SECONDARIES:
                print("UNKNOWN SECONDARY", effect["volatileStatus"])
            else:
                self.secondaries[effect["volatileStatus"]] = effect["chance"]
        elif "self" in effect:
            if "boosts" in effect["self"]:
                for stat, val in effect["self"]["boosts"].items():
                    if stat not in self.auto_boosts:
                        print("stat in auto boost", stat)
                    self.auto_boosts[stat] = (val, effect["chance"])
            else:
                print("effect self", effect)
        else:
            effect.pop("chance")
            if effect:
                print("effect", effect)

    @property
    def dic_state(self) -> dict:
        """
        dict: dictionnary describing the object's state
        """
        return {
            "accuracy": self.accuracy,
            "auto_boosts": self.auto_boosts,
            "base_power": self.base_power,
            "boosts": self.boosts,
            "category": {
                category: category == self.category for category in CATEGORIES
            },
            "exists": 1,
            "max_pp": self.max_pp,
            "priority": self.priority,
            "target": {target: target == self.target for target in TARGETS},
            "type": {type_: type_ == self.type for type_ in TYPES},
            "secondaries": self.secondaries,
            "z_boost": self.z_boost,
            "z_power": self.z_power,
            "z_effect": self.z_effect,
        }


class ZMoveException(Exception):
    """
    Exception raised when a Move class is instantiated from a ZMove
    """
    pass
