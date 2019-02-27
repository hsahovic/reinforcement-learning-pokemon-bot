import json

global POKEDEX

with open("data/pokedex.json") as f:
    POKEDEX = json.load(f)


class Pokemon:
    def __init__(self, *, ident: str = None, opponents=False) -> None:
        self.species = "".join(
            [
                char
                for char in ident.split(": ")[-1].lower()
                if char in "abcdefghijklmnopqrstuvwxyz0123456789"
            ]
        )

        # self.id = ident.split(": ")[-1].lower().split("-")[0] # Identity without player number
        self.ability = POKEDEX[self.species]["abilities"]
        self.attracted = False
        self.active = None
        self.base_stats = POKEDEX[self.species]["baseStats"]
        self.confused = False
        self.current_hp = None
        self.encored = False
        self.focused = False
        self.infested = False
        self.item = None
        self.level = None
        self.leech_seeding = False
        self.max_hp = None
        self.mega = False
        self.moves = None
        self.opponents = opponents
        self.perish_count = 4
        self.primal = False
        self.sex = None
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
        self.types = POKEDEX[self.species]["types"]
        self.type_changed = None
        self.yawned = False

        self.ident = ident
        self.reset_stat_boosts()
        self.set_form(self.species)

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

    def reset_stat_boosts(
        self, clear_neg: bool = False, clear_pos: bool = False
    ) -> None:
        if clear_neg:
            self.boosts = {key: max(0, val) for key, val in self.boosts.items()}
        elif clear_pos:
            self.boosts = {key: min(0, val) for key, val in self.boosts.items()}
        else:
            self.boosts = {
                "atk": 0,
                "spa": 0,
                "def": 0,
                "spd": 0,
                "spe": 0,
                "fnt": 0,
                "accuracy": 0,
                "evasion": 0,
            }

    def set_form(
        self,
        form: str = None,
        *,
        mega: bool = False,
        primal: bool = False,
        complement: str = "",
    ) -> None:
        if mega:
            form = self.species.lower() + "mega" + complement
        elif primal:
            form = self.species.lower() + "primal"
        else:
            form = "".join(
                [
                    char
                    for char in form.lower()
                    if char in "abcdefghijklmnopqrstuvwxyz0123456789"
                ]
            )
        self.ability = POKEDEX[form]["abilities"]
        self.base_stats = POKEDEX[form]["baseStats"]
        self.types = POKEDEX[form]["types"]
        self.num = POKEDEX[form]["num"]

    def set_status(self, status: str, cure: bool = False) -> None:
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
            self.status["fnt"] = True
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
