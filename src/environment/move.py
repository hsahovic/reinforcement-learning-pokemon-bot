from environment.utils import CATEGORIES, MOVES, TARGETS, TYPES, SECONDARIES


empty_move = {
    "accuracy": 0,
    "auto_boosts": {
        "tox": (0, 0),
        "psn": (0, 0),
        "slp": (0, 0),
        "par": (0, 0),
        "brn": (0, 0),
        "frz": (0, 0),
    },
    "base_power": 0,
    "boosts": {
        "tox": (0, 0),
        "psn": (0, 0),
        "slp": (0, 0),
        "par": (0, 0),
        "brn": (0, 0),
        "frz": (0, 0),
    },
    "category": {category: False for category in CATEGORIES},
    "exists": 0,
    "max_pp": 0,
    "priority": 0,
    "target": {target: False for target in TARGETS},
    "type": {type_: False for type_ in TYPES},
    "secondaries": {
        "par": 0,
        "brn": 0,
        "frz": 0,
        "psn": 0,
        "slp": 0,
        "flinch": 0,
        "confusion": 0,
    },
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


class Move:
    def __init__(self, move) -> None:
        move = "".join([char for char in move if char not in "-' "])
        if move.startswith("hiddenpower") and move[-1] in "0123456789":
            move = move[:-2]

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
        # TODO : add pp management ?
        self.priority = MOVES[move]["priority"]
        # TODO right now we can ignore flags
        self.flags = MOVES[move]["flags"]
        self.boosts = {
            "tox": (0, 0),
            "psn": (0, 0),
            "slp": (0, 0),
            "par": (0, 0),
            "brn": (0, 0),
            "frz": (0, 0),
        }
        self.auto_boosts = {
            "tox": (0, 0),
            "psn": (0, 0),
            "slp": (0, 0),
            "par": (0, 0),
            "brn": (0, 0),
            "frz": (0, 0),
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
        # TODO
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
        # TODO : proper z move effect management
        if "zMoveEffect" in MOVES[move]:
            self.z_effect = True
        else:
            self.z_effect = False

    def __repr__(self) -> str:
        return f"Move object: {self.name}"

    def add_secondary(self, effect):
        self.name
        if "boosts" in effect:
            for stat, val in effect["boosts"].items():
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
                    self.auto_boosts[stat] = (val, effect["chance"])
            else:
                print("effect self", effect)
        else:
            effect.pop("chance")
            if effect:
                print("effect", effect)

    @property
    def dic_state(self) -> dict:
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
    pass
