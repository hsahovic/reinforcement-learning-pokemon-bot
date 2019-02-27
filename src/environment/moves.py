import json

global MOVES

with open("data/moves.json") as f:
    MOVES = json.load(f)


class Move:
    def __init__(self, *, ident: str = None) -> None:

        self.ident = ident
        # try:
        self.num = MOVES[self.ident]["num"]
        # except :
        # self.num = 100
        self.accuracy = (
            MOVES[self.ident]["accuracy"]
            if not isinstance(MOVES[self.ident]["accuracy"], bool)
            else 100
        )
        self.base_power = MOVES[self.ident]["basePower"]
        self.category = MOVES[self.ident]["category"]
        # try:
        #     self.desc = MOVES[self.ident]["desc"]
        # except:
        #     self.desc = ""
        # self.short_desc = MOVES[self.ident]["shortDesc"]
        self.name = MOVES[self.ident]["name"]
        self.max_pp = MOVES[self.ident]["pp"]
        self.priority = MOVES[self.ident]["priority"]
        self.flags = MOVES[self.ident]["flags"]
        # try:
        self.secondary = (
            MOVES[self.ident]["secondary"]
            if not isinstance(MOVES[self.ident]["accuracy"], bool)
            else {}
        )
        # except:
        # self.secondary = {}
        self.target = MOVES[self.ident]["target"]
        self.type = MOVES[self.ident]["type"]
        # self.contestType = MOVES[self.ident]["contestType"]

    def __repr__(self) -> str:
        return f"Move object: {self.name}"
