# -*- coding: utf-8 -*-
"""
Battle class. Represents, from a player's perspective, the state of a Pokemon battle.

This file is part of the pokemon showdown reinforcement learning bot project,
created by Randy Kotti, Ombeline Lagé and Haris Sahovic as part of their
advanced topics in artifical intelligence course at Ecole Polytechnique.

# TODO:
- Extend to double battles
- Expand parsing to take into account all types of messages
- Check player identity definition and update, especially in _get_pokemon_from_reference
- Check parse in detail
- In parse_request, manage ultra boost
- Parse turn id in parse_request
"""

from environment.pokemon import empty_pokemon, Pokemon, Move
from typing import List


class Battle:
    """
    Represents the state of a Pokemon battle for a given player.
    """

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
    """List of str: contain types of messages to ignore while parsing"""

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
    """List of str: contain possible fields statuses"""

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
    """List of str: contain possible weather statuses"""

    def __init__(self, battle_tag: str, player_name: str) -> None:
        """Battle __init__

        This methods initialises most battle attributes. It records the player's 
        name and battle tag.

        Args:
            attle_tag1 (str): The battle tag, as extracted from showdown
            
            player_name (str): The battle's player name.
        """

        # Simple pre-formatting
        while battle_tag.endswith("\n"):
            battle_tag = battle_tag[:-1]

        # Teams attributes
        self._player_team = {}
        self._opponent_team = {}
        self._player_team_size = None
        self._opponent_team_size = None

        if battle_tag.startswith(">"):
            battle_tag = battle_tag[1:]
        self._battle_tag = battle_tag

        # End of battle attributes
        self._finished = False
        self._winner = None
        self._won = None

        # This is stored for future extension
        self._gametype = None

        # Some basic information on the battle
        self._player_name = player_name
        self._player_role = None
        self._turn = 0

        # Field and weather information
        self._weather = "none"
        self.p1_fields = {field: False for field in self.FIELDS}
        self.p2_fields = {field: False for field in self.FIELDS}

        self._wait = False

        self._recorded_moves = {"context": [], "decision": []}

    def _get_pokemon_from_reference(self, reference: str) -> Pokemon:
        """Returns a pokemon from a reference
        
        The player and pokemon are inferred from the reference. If the pokemon is 
        already created, it is returned. Otherwise, it is added to its player team and
        then returned.

        Args:
            reference (str): the reference, as it appears in the message system

        Returns:
            The Pokemon object corresponding to the reference
        """
        player, pokemon_ident = reference[:2], reference.split(": ")[-1]

        if (player == self._player_role) or (
            self._player_role is None
        ):  # this is a hack ; apparently it happens on battle init. This needs to be looked into.
            if pokemon_ident not in self._player_team:
                self._player_team[pokemon_ident] = Pokemon(ident=pokemon_ident)
            return self._player_team[pokemon_ident]
        elif player is not None:
            if pokemon_ident not in self._opponent_team:
                self._opponent_team[pokemon_ident] = Pokemon(
                    ident=pokemon_ident, opponents=True
                )
            return self._opponent_team[pokemon_ident]

    def parse_message(self, message: List[str]) -> None:
        """
        Update the object from a message

        Args:
            message (list of str): split message to be parsed
        """
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

    def parse_request(self, request: dict) -> None:
        """
        Update the object from a request.

        The player's pokemon are all updated, as well as available moves, switches and
        other related information (z move, mega evolution, forced switch...).

        Args:
            request (dict): parsed json request object
        """
        if "wait" in request and request["wait"]:
            self._wait = True
        else:
            self._wait = False

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
            if "canMegaEvo" in active and active["canMegaEvo"]:
                self.can_mega_evolve = True
            if "canZMove" in active:
                self.can_z_move = active["canZMove"]
            if "maybeTrapped" in active:
                active["maybeTrapped"]

        side = request["side"]
        if not self.trapped:
            for i, pokemon in enumerate(side["pokemon"]):
                if not pokemon["active"] and pokemon["condition"] != "0 fnt":
                    self.available_switches.append((i + 1, pokemon["ident"]))

        for pokemon_info in side["pokemon"]:
            pokemon = self._get_pokemon_from_reference(pokemon_info["ident"])
            pokemon.update_from_request(pokemon_info)

        self._turn += 1

    def player_is_p1(self) -> None:
        """
        Sets the battle's player to p1
        """
        self._player_role = "p1"

    def player_is_p2(self) -> None:
        """
        Sets the battle's player to p2
        """
        self._player_role = "p2"

    def record_move(self, context, move: int) -> None:
        """
        Record move information in the battle.

        Args:
            context (arbitrary): the information regarding the context that led to the
            move choice that we want to store. From a ML point of view, it corresponds
            to the input x.
            
            move (int): choice id. From a ML point of view, it corresponds to the output
            y.
        """
        self._recorded_moves["context"].append(context)
        self._recorded_moves["decision"].append(move)

    def won_by(self, winner: str) -> None:
        """
        Update the battle's winner.

        Args:
            winner (str): player identifier
        """
        self._finished = True
        self._winner = winner
        self._won = self._player_name == winner

    @property
    def active_moves(self) -> List[str]:
        """
        List of str: the active pokemon's moves
        """
        active = self.active_pokemon
        if active:
            return list(active.moves.keys())
        else:
            return []

    @property
    def active_pokemon(self) -> Pokemon:
        """
        Pokemon: the active pokemon, or None
        """
        for pokemon in self._player_team.values():
            if pokemon.active:
                return pokemon
        return None

    @property
    def available_moves_object(self) -> List[Move]:
        """
        List of Move: list of available moves objects
        """
        return [Move(move["id"]) for _, move in self.available_moves]

    @property
    def available_switches_object(self) -> Pokemon:
        """
        List of Pokemon: list of available switches as Pokemon objects
        """
        return [
            self._get_pokemon_from_reference(ident)
            for _, ident in self.available_switches
        ]

    @property
    def battle_tag(self) -> str:
        """
        str: battle's battle_tag
        """
        return self._battle_tag

    @property
    def dic_state(self) -> dict:
        """
        dict: dictionnary describing the object's state
        """
        active = self.active_pokemon
        opponent_active = self.opponent_active_pokemon

        back = [
            pokemon.dic_state
            for pokemon in self._player_team.values()
            if not pokemon.active
        ]
        opponent_back = [
            pokemon.dic_state
            for pokemon in self._opponent_team.values()
            if not pokemon.active
        ]

        if not active:
            active = empty_pokemon
        else:
            active = active.dic_state
        if not opponent_active:
            opponent_active = empty_pokemon
        else:
            opponent_active = opponent_active.dic_state

        while len(back) < 5:
            back.append(empty_pokemon)
        while len(opponent_back) < 5:
            opponent_back.append(empty_pokemon)

        return {
            "active": active,
            "opponent_active": opponent_active,
            "back": back,
            "opponent_back": opponent_back,
            "weather": {weather: self._weather == weather for weather in self.WEATHERS},
            "field": self.p1_fields if self._player_role == "p1" else self.p2_fields,
            "opponent_field": self.p2_fields
            if self._player_role == "p1"
            else self.p1_fields,
        }

    @property
    def is_ready(self) -> bool:
        """
        bool: indicated if the battle is initialised, with an identified player and a
        team
        """
        return (self._player_role is not None) and self._player_team

    @property
    def moves_data(self) -> dict:
        """
        dict: stored moves information
        """
        return self._recorded_moves

    @property
    def opponent_active_pokemon(self) -> Pokemon:
        """
        Pokemon: the opponent's active pokemon, or None
        """
        for pokemon in self._opponent_team.values():
            if pokemon.active:
                return pokemon
        return None

    @property
    def opponent_player_back(self) -> List[str]:
        """
        List of str: the player's back pokemons' species names
        """
        return [
            pokemon.species
            for pokemon in self._opponent_team.values()
            if not pokemon.active
        ]

    @property
    def player_back(self) -> List[str]:
        """
        List of str: the player's back pokemons' species names
        """
        return [
            pokemon.species
            for pokemon in self._player_team.values()
            if not pokemon.active
        ]

    @property
    def turn_sent(self) -> int:
        """
        int: turn identifier to send when choosing a move
        """
        return self._turn * 2 + (1 if self._player_role == "p2" else 0)

    @property
    def wait(self) -> bool:
        """
        bool: indicates if the last requested requiered waiting
        """
        return self._wait

    @property
    def winning_moves_data(self) -> dict:
        """
        dict: stored winning moves information
        """
        if self._won:
            return self.recorded_moves
        else:
            return {"context": [], "decision": []}

    @property
    def won(self) -> bool:
        """
        bool: indicates if the battle was won by the player
        """
        return self._won
