import json

global MOVES

with open("data/moves.json") as f:
    MOVES = json.load(f)


# These are magic regexes to convert from the .js moves file to working json, when
# combined with some auto-formatting
# ^    "((on.*)|(.*Callback))": function\(.*?\) {\n(.*\n)*?    },\n
# ^      "((on.*)|(.*Callback))": function\(.*?\) {\n(.*\n)*?      },?\n
# ^        "((on.*)|(.*Callback))": function\(.*?\) {\n(.*\n)*?        },?\n
# //.*

class Move:

    SECONDARIES = []

    def __init__(self, move) -> None:
        return
        print(move)
        move = ''.join([char for char in move if char not in '- '])
        if move.startswith('hiddenpower') and move[-1] in '0123456789':
            move = move[:-2] 

        self.name = move
        self.accuracy = (
            MOVES[move]["accuracy"]
            if not isinstance(MOVES[move]["accuracy"], bool)
            else 100
        )
        self.base_power = MOVES[move]["basePower"]
        self.category = MOVES[move]["category"]
        self.max_pp = MOVES[move]["pp"]
        # TODO : add pp management ?
        self.priority = MOVES[move]["priority"]
        # TODO
        self.flags = MOVES[move]["flags"]
        
        self.secondaries = {}
        if 'secondary' in MOVES[move]:
            if MOVES[move]['secondary']:
                self.add_secondary(MOVES[move]['secondary'])
        elif 'secondaries' in MOVES[move]:
            for secondary in MOVES[move]['secondaries']:
                self.add_secondary(secondary)
        
        # TODO
        self.target = MOVES[move]["target"]
        # TODO
        self.type = MOVES[move]["type"].lower()

    def __repr__(self) -> str:
        return f"Move object: {self.name}"

    def add_secondary(self, effect):
        if 'boosts' in effect:
            for stat, val in effect['boosts'].items:
                self.secondaries[stat + val] = effect['chance']
        else:
            print(effect)