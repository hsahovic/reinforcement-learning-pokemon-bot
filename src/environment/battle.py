from environment.pokemon import empty_pokemon, Pokemon, Move
from pprint import pprint
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
        "-miss",
        "-mustrecharge",
        "-prepare",  # TODO : switch to an actual boolean somewhere, this needs to be used properly
        "-resisted",
        "-singlemove",  # TODO : check single move possibilities
        "-singleturn",  # TODO : check single turn possibilities
        "-supereffective",
        "-transform",
        "-zbroken",  # TODO : what is this ?
        "-zpower",  # TODO : item assignment ?
        "cant",
        "deinit",
        "detailschange",
        "drag",
        "gen",
        "init",
        "j",
        "l",
        "player",
        "rule",
        "seed",
        "start",
        "swap",
        "replace",
        "tier",
        "title",
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
        # TODO : check that this actually works
        # message_list = message.split(": ")
        # player, ident = message_list[0], message_list[1]
        player, ident = message[:2], message.split(": ")[-1]
        if (player == self._player_role) or (self._player_role is None): # this is a hack ; apparently it happens on battle init. This needs to be looked into.
            if ident not in self._player_team:
                self._player_team[ident] = Pokemon(ident=ident)
            return self._player_team[ident]
        else:
            if ident not in self._opponent_team:
                self._opponent_team[ident] = Pokemon(ident=ident, opponents=True)
            return self._opponent_team[ident]

    def parse(self, message: List[str]) -> None:
        if message[1] in self.ACTIONS_TO_IGNORE:
            return
        elif message[1] == "switch":
            if message[2][0:2] == self._player_role:
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
        elif message[1] == "callback" and message[2] == "trapped":
            self.trapped = True
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.set_status(message[3], cure=True)
        elif message[1] == "-curestatus":
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.set_status(message[3], cure=True)
        elif message[1] == "-clearallboost":
            for pokemon in self._opponent_team.values():
                pokemon.reset_stat_boosts()
            for pokemon in self._player_team.values():
                pokemon.reset_stat_boosts()
        elif message[1] == "move":
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.update_from_move(message[3])
        elif message[1] == "faint":
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.set_status("fnt")
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
        elif message[1] == "-mega":
            complement = "x" if message[4][-1] == "X" else ""
            complement = "y" if message[4][-1] == "Y" else complement
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.set_form(mega=True, complement=complement)
        elif message[1] == "-primal":
            pokemon = self._get_pokemon_from_reference(message[2])
            pokemon.set_form(primal=True)
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
        if "wait" in request and request["wait"]:
            self.wait = True
        else:
            self.wait = False

        self.available_moves = []
        self.available_switches = []
        self.can_mega_evolve = False
        self.can_z_move = False
        self.trapped = False

        if "active" in request:
            active = request["active"][0]
            if "trapped" in active and active["trapped"]:
                self.trapped = True
            for i, move in enumerate(active["moves"]):
                if "disabled" not in move or not move["disabled"]:
                    self.available_moves.append((i + 1, move))
                    # self.available_moves.append((i + 1, Move(move["id"])))
            if "canMegaEvo" in active and active["canMegaEvo"]:
                self.can_mega_evolve = True
            if "canZMove" in active:
                self.can_z_move = active["canZMove"]
            if "maybeTrapped" in active:
                active["maybeTrapped"]
            if "canUltraBurst" in active:
                pass
                # active["canUltraBurst"]  # TODO : check this

        side = request["side"]
        if not self.trapped:
            for i, pokemon in enumerate(side["pokemon"]):
                if not pokemon["active"] and pokemon["condition"] != "0 fnt":
                    self.available_switches.append((i + 1, pokemon["ident"]))
                    # self.available_switches.append((i + 1, Pokemon(ident=pokemon["ident"])))
                    # self.available_switches[-1][1].update_from_request(pokemon)

        for pokemon_info in side["pokemon"]:
            pokemon = self._get_pokemon_from_reference(pokemon_info["ident"])
            pokemon.update_from_request(pokemon_info)

        request["rqid"]
        if "forceSwitch" in request:
            request["forceSwitch"]
        if "noCancel" in request:
            request["noCancel"]
        if "maybeTrapped" in request:
            request["maybeTrapped"]

        self._turn += 1

    def won_by(self, winner: str) -> None:
        self._finished = True
        self._winner = winner
        self._won = self._player_name == winner

    @property
    def active_moves(self) -> List[str]:
        active = [
            pokemon
            for pokemon in self._player_team.values()
            if pokemon.active
        ][0]
        return list(active.moves.keys())

    @property
    def active_pokemon(self) -> Pokemon:    
        for pokemon in self._player_team.values():
            if pokemon.active:
                return pokemon
        return None

    @property
    def available_moves_object(self) -> Move:
        moves = []
        for _, move in self.available_moves:
            moves.append(Move(move['id']))
        return moves

    @property
    def available_switches_object(self) -> Pokemon:
        switches = []
        for _, ident in self.available_switches:
            switches.append(self._player_team[ident.split(': ')[-1]])
        return switches

    @property
    def battle_tag(self) -> str:
        return self._battle_tag

    @property
    def dic_state(self) -> dict:
        active = [
            pokemon.dic_state
            for pokemon in self._player_team.values()
            if pokemon.active
        ]
        opp_active = [
            pokemon.dic_state
            for pokemon in self._opponent_team.values()
            if pokemon.active
        ]
        back = [
            pokemon.dic_state
            for pokemon in self._player_team.values()
            if not pokemon.active
        ]
        opp_back = [
            pokemon.dic_state
            for pokemon in self._opponent_team.values()
            if not pokemon.active
        ]

        if not active:
            active = empty_pokemon
        else:
            active = active[0]
        if not opp_active:
            opp_active = empty_pokemon
        else:
            opp_active = opp_active[0]
        while len(back) < 5:
            back.append(empty_pokemon)
        while len(opp_back) < 5:
            opp_back.append(empty_pokemon)

        return {
            "active": active,
            "opp_active": opp_active,
            "back": back,
            "opp_back": opp_back,
            "weather": {weather: self._weather == weather for weather in self.WEATHERS},
            "field": self.p1_fields if self._player_role == "p1" else self.p2_fields,
            "opp_field": self.p2_fields
            if self._player_role == "p1"
            else self.p1_fields,
        }
        
    @property
    def opp_active_pokemon(self) -> Pokemon:
        for pokemon in self._opponent_team.values():
            if pokemon.active:
                return pokemon
        return None

    @property
    def player_back(self) -> List[str]:
        return [pokemon.species for pokemon in self._player_team.values() if not pokemon.active]

    @property
    def is_ready(self) -> bool:
        return (self._player_role is not None) and self._player_team

    @property
    def turn_sent(self) -> int:
        return self._turn * 2 + (1 if self._player_role == "p2" else 0)
