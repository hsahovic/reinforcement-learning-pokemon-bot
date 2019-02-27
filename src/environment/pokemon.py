import json


class Pokemon:
    with open('data/pokedex.json') as f:
        pokedex = json.load(f)
    
    def __init__(self, *, ident: str = None, opponents=False) -> None:
        self.ident = ident
        self.ability = Pokemon.pokedex[self.ident]["abilities"]
        self.attracted = False
        self.active = None
        self.confused = False
        self.current_hp = Pokemon.pokedex[self.ident]["baseStats"]["hp"]
        self.encored = False
        self.focused = False
        self.infested = False
        self.item = None
        self.level = None
        self.leech_seeding = False
        self.max_hp = Pokemon.pokedex[self.ident]["baseStats"]["hp"]
        self.mega = False
        self.moves = None
        self.num = Pokemon.pokedex[self.ident]["num"]
        self.opponents = opponents
        self.perish_count = 4
        self.sex = None
        self.species = Pokemon.pokedex[self.ident]["species"]
        self.stats = None
        self.status = {
            "tox": False,
            "psn": False,
            "slp": False,
            "par": False,
            "brn": False,
            "frz": False,
        }
        self.substitute = False
        self.taunted = False
        self.types = Pokemon.pokedex[self.ident]["types"]
        self.type_changed = None
        self.yawned = False

        self.reset_stat_boosts()

    def __repr__(self) -> str:
        return f"Pokemon object: {self.species} ({self.current_hp}/{self.max_hp})"

    def _update_formatted_details(self, details: str) -> None:
        details = details.split(", ")
        if len(details) == 3:
            self.species, self.level, self.sex = details
        elif len(details) == 2:
            self.species, self.level = details
            self.sex = None
        else:
            self.species = details[0]
            self.sex = None
            self.level = 100

    def boost(self, stat: str, value: int) -> None:
        self.boosts[stat] += value

    def reset_stat_boosts(self, clear_neg=False, clear_pos=False) -> None:
        if clear_neg:
            self.boosts = {key: max(0, val) for key, val in self.boosts.items()}
        elif clear_pos:
            self.boosts = {key: min(0, val) for key, val in self.boosts.items()}
        else:
            self.boosts = {
                "atk": Pokemon.pokedex[self.ident]["baseStats"]["atk"],
                "spa": Pokemon.pokedex[self.ident]["baseStats"]["spa"],
                "def": Pokemon.pokedex[self.ident]["baseStats"]["def"],
                "spd": Pokemon.pokedex[self.ident]["baseStats"]["spd"],
                "spe": Pokemon.pokedex[self.ident]["baseStats"]["spe"],
                "accuracy": 0,
                "evasion": 0,
            }

    def set_form(self, form: str) -> None:
        # TODO : manage form transformations
        pass

    def set_status(self, status: str, cure=False) -> None:
        if status not in self.status:
            # TODO : at some point, get rid of this
            print(f"UNKNOWN STATUS {status}")
        if cure:
            self.status[status] = False
        else:
            self.status[status] = True

    def update_formatted_condition(self, condition: str) -> None:
        if condition == "0 fnt":
            # TODO : switch to enum ?
            self.status = "fnt"
            self.current_hp = 0
        else:
            if condition[-1] not in "1234567890":
                self.status[condition[-3:]] = True
                condition = condition[:-4]
            self.current_hp, self.max_hp = [int(el) for el in condition.split("/")]

    def update_from_request(self, request: dict) -> None:
        assert self.ident == request.pop("ident")

        self._update_formatted_details(request.pop("details"))
        self.update_formatted_condition(request.pop("condition"))

        self.ability = request.pop("baseAbility")
        self.attracted = False
        self.active = request.pop("active")
        self.focused = False
        self.item = request.pop("item")
        self.moves = request.pop("moves")
        self.stats = request.pop("stats")

        request.pop("pokeball")
        request.pop("ability")

        if request:
            print(request)

    def update_from_switch(self, message: str) -> None:
        self.update_formatted_condition(message[-1])
        self._update_formatted_details(message[-2])

        self.reset_stat_boosts()

        self.active = True
        self.confused = False
        self.encored = False
        self.infested = False
        self.perish_count = 4
        self.substitute = False
        self.taunted = False
        self.type_changed = None