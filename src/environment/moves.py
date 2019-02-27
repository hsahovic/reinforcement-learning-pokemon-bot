import json

class Move:
    with open('data/moves.json') as f:
        moves = json.load(f)

    def __init__(self, *, ident: str = None) -> None:

        self.ident = ident
        try:
            self.num = Move.moves[self.ident]["num"]
        except:
            self.num = 100
        self.accuracy = (Move.moves[self.ident]["accuracy"] if not isinstance(
            Move.moves[self.ident]["accuracy"], bool) else 100)
        self.basePower = Move.moves[self.ident]["basePower"]
        self.category = Move.moves[self.ident]["category"]
        try:
            self.desc = Move.moves[self.ident]["desc"]
        except:
            self.desc = ""
        self.shortDesc = Move.moves[self.ident]["shortDesc"]
        self.name = Move.moves[self.ident]["name"]
        self.pp = Move.moves[self.ident]["pp"]
        self.priority = Move.moves[self.ident]["priority"]
        self.flags = Move.moves[self.ident]["flags"]
        try:
            self.secondary = (Move.moves[self.ident]["secondary"] if not isinstance(
                Move.moves[self.ident]["accuracy"], bool) else {})
        except:
            self.secondary = {}
        self.target = Move.moves[self.ident]["target"]
        self.type = Move.moves[self.ident]["type"]
        self.contestType = Move.moves[self.ident]["contestType"]

    def __repr__(self) -> str:
        return f"Move object: {self.name}"