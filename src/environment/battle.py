from environment.pokemon import Pokemon
from typing import List, Tuple


class Battle:

    ACTIONS_TO_IGNORE = [
        "",
        "-ability",
        "-activate",
        "-anim",
        "-center",
        "-crit",
        "-cureteam",
        "-damage",
        "-endability",
        "-enditem",
        "-fail",
        "-fieldactivate",
        "-fieldend",
        "-fieldstart",
        "-heal",
        "-hint",
        "-hitcount",
        "-immune",
        "-item",
        "-message",
        "-miss",  # TODO : check misses
        "-mustrecharge",
        "-prepare",  # TODO : switch to an actual boolean somewhere, this needs to be used properly
        "-resisted",
        "-singlemove",  # TODO : check single move possibilities
        "-singleturn",  # TODO : check single turn possibilities
        "-supereffective",
        "-transform",
        "-zbroken", # TODO : what is this ?
        "-zpower",  # TODO : item assignment ?
        "callback",  # TODO
        "cant",
        "deinit",
        "detailschange",
        "drag",
        "faint",
        "gen",
        "init",
        "j",
        "l",
        "move",
        "player",
        "rule",
        "seed",
        "start",
        "swap",
        "replace",
        "tier",
        "title",
        "turn",
        "upkeep",
    ]

    FIELDS = [
        "Aurora Veil",
        "Light Screen",
        "Reflect",
        "Safeguard",
        "Spikes",
        "Stealth Rock",
        "Sticky Web",
        "Tailwind",
        "Toxic Spikes",
    ]

    WEATHERS = [
        "none",
        "DesolateLand",
        "Hail",
        "PrimordialSea",
        "RainDance",
        "Safeguard",
        "Sandstorm",
        "SunnyDay",
    ]

    def __init__(self, battle_tag: str, player_name: str) -> None:
        while battle_tag.endswith("\n"):
            battle_tag = battle_tag[:-1]

        self._player_team = {}
        self._opponent_team = {}
        self._player_team_size = None
        self._opponent_team_size = None

        if battle_tag.startswith(">"):
            battle_tag = battle_tag[1:]
        self._battle_tag = battle_tag

        self._finished = False
        self._winner = None
        self._won = None

        self._gametype = None

        self._player_name = player_name
        self._player_role = None
        self._turn = 0

        self._weather = "none"
        self.p1_fields = {field: False for field in self.FIELDS}
        self.p2_fields = {field: False for field in self.FIELDS}

        self.wait = False

    def _get_pokemon_from_reference(self, message: str) -> Pokemon:
        player, ident = message[2][:2], message[2][:2] + message[2][3:]
        if player == self._player_role:
            if ident not in self._player_team:
                self._player_team[ident] = Pokemon(ident=ident)
            return self._player_team[ident]
        else:
            if ident not in self._opponent_team:
                self._opponent_team[ident] = Pokemon(ident=ident, opponents=True)
            return self._opponent_team[ident]

    def parse(self, message: List[str]) -> None:

        # TODO : clean the debugs

        if message[1] in self.ACTIONS_TO_IGNORE:
            return
        elif message[1] == "switch":
            if message[0:2] == self._player_role:
                for pokemon in self._player_team.values():
                    pokemon.active = False
            else:
                for pokemon in self._opponent_team.values():
                    pokemon.active = False
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.update_from_switch(message)
        elif message[1] == "gametype":
            self._gametype = message[2]
        elif message[1] == "teamsize":
            if message[2] == self._player_role:
                self._player_team_size = int(message[3])
            else:
                self._opponent_team_size = int(message[3])
        elif message[1] == "-boost":
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.boost(message[3], int(message[4]))
        elif message[1] == "-unboost":
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.boost(message[3], -int(message[4]))
        elif message[1] == "-status":
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.set_status(message[3])
        elif message[1] == "-curestatus":
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.set_status(message[3], cure=True)
        elif message[1] == "-clearallboost":
            for pokemon in self._opponent_team.values():
                pokemon.reset_stat_boosts()
            for pokemon in self._player_team.values():
                pokemon.reset_stat_boosts()
        elif message[1] == "-clearboost":
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.reset_stat_boosts()
        elif message[1] == "-formechange":
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.set_form(message[3])
        elif message[1] == "-clearnegativeboost":
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.reset_stat_boosts(clear_neg=True)
        elif message[1] == "-clearpositiveboost":
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.reset_stat_boosts(clear_pos=True)
        elif message[1] == "-setboost":
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.boosts[message[3]] = int(message[4])
        elif message[1] in ["-mega", "-primal"]:  # TODO : check primal / mega
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.mega = True
        elif message[1] == "-sethp":
            self._get_pokemon_from_reference(message[2]).update_formatted_condition(
                message[3]
            )
            self._get_pokemon_from_reference(message[4]).update_formatted_condition(
                message[5]
            )
        elif message[1] in ["-sidestart", "-sideend"]:
            value = message[1] == "-sidestart"
            if message[3].startswith("move: "):
                message[3] = message[3][6:]
            if message[3] not in self.FIELDS:
                print("unmanaged battle message:", "|".join(message), self.battle_tag)
                raise Exception(message[3])
            if message[1] == "1":
                self.p1_fields[message[3]] = value
            else:
                self.p2_fields[message[3]] = value
        elif message[1] in ["-start", "-end"]:
            value = message[1] == "-start"
            pokemon = self._get_pokemon_from_reference(message[2])
            if message[3].startswith("move: "):
                message[3] = message[3][6:]
            if message[3].startswith("ability: "):
                message[3] = message[3][9:]
            if message[3] == "Substitute":
                pokemon.substitute = value
            elif message[3] == "Focus Energy":
                pokemon.focused = value
            elif message[3] == "Attract":
                pokemon.attracted = value
            elif message[3] == "confusion":
                pokemon.confusion = value
            elif message[3] == "Encore":
                pokemon.encored = value
            elif message[3] == "Infestation":
                pokemon.infested = value
            elif message[3] == "Leech Seed":
                pokemon.leech_seeding = value
            elif message[3] == "Yawn":
                pokemon.yawned = value
            elif message[3] in [
                "Autotomize",
                "Magnet Rise",
                "Illusion",
                "Slow Start",
                "Flash Fire",
                "Smack Down",
                "Disable",
            ]:  # TODO : illusion, flashfire, smack down, disable ?
                pass
            elif message[3] == "Taunt":
                pokemon.taunted = value
            elif message[3] == "typechange":  # TODO : info on origin ?
                pokemon.typechange = message[4]
            elif message[3].startswith("perish"):
                pokemon.perish_count = int(message[3][-1])
            else:
                print("unmanaged battle message:", "|".join(message), self.battle_tag)
        elif message[1] == "-weather":
            if message[2] not in self.WEATHERS:
                print("unmanaged battle message:", "|".join(message), self.battle_tag)
                raise Exception(message[2])
            else:
                self._weather = message[2]
        else:
            print("unmanaged battle message:", "|".join(message), self.battle_tag)

    def player_is_p1(self) -> None:
        self._player_role = "p1"

    def player_is_p2(self) -> None:
        self._player_role = "p2"

    def update_from_request(self, request: dict) -> None:
        if "wait" in request and request.pop("wait"):
            self.wait = True
        else:
            self.wait = False

        self.available_moves = []
        self.available_switches = []
        self.can_mega_evolve = False
        self.can_z_move = False
        self.trapped = False

        # TODO : clean exploratory prints

        if "active" in request:
            active = request.pop("active")
            assert len(active) == 1
            active = active[0]
            if "trapped" in active and active.pop("trapped"):
                self.trapped = True
            for i, move in enumerate(active.pop("moves")):
                if "disabled" not in move or not move["disabled"]:
                    self.available_moves.append((i + 1, move))
            if "canMegaEvo" in active and active.pop("canMegaEvo"):
                self.can_mega_evolve = True
            if "canZMove" in active:
                self.can_z_move = active.pop("canZMove")
            if "maybeTrapped" in active:
                active.pop("maybeTrapped")
            if "canUltraBurst" in active:
                active.pop("canUltraBurst")  # TODO : check this
            if active:
                print("active", active)

        side = request.pop("side")
        if not self.trapped:
            for i, pokemon in enumerate(side["pokemon"]):
                if not pokemon["active"] and pokemon["condition"] != "0 fnt":
                    self.available_switches.append((i + 1, pokemon["ident"]))

        for pokemon_info in side["pokemon"]:
            if pokemon_info["ident"] not in self._player_team:
                self._player_team[pokemon_info["ident"]] = Pokemon(
                    ident=pokemon_info["ident"]
                )
            self._player_team[pokemon_info["ident"]].update_from_request(pokemon_info)

        request.pop("rqid")
        if "forceSwitch" in request:
            request.pop("forceSwitch")
        if "noCancel" in request:
            request.pop("noCancel")
        if "maybeTrapped" in request:
            request.pop("maybeTrapped")

        if request:
            print("request", request)

        self._turn += 1

    def won_by(self, winner: str) -> None:
        self._finished = True
        self._winner = winner
        self._won = self._player_name == winner

    @property
    def battle_tag(self) -> str:
        return self._battle_tag

    @property
    def is_ready(self) -> bool:
        return (self._player_role is not None) and self._player_team

    @property
    def turn_sent(self) -> int:
        return self._turn * 2 + (1 if self._player_role == "p2" else 0)
