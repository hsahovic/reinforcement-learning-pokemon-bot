from environment.pokemon import Pokemon
from typing import List

class Battle:

    ACTIONS_TO_IGNORE = [
        "",
        "-ability",
        "-activate",
        "-center",
        "-crit",
        "-cureteam",
        "-damage",
        "-endability",
        "-enditem",
        "-fail",
        "-fieldend",
        "-fieldstart",
        "-heal",
        "-hint",
        "-immune",
        "-item",
        "-mega",
        "-message",
        "-resisted",
        "-supereffective",
        "-transform",
        "cant",
        "detailschange",
        "faint",
        "init",
        "j",
        "move",
        "player",
        "title",
        "turn",
        "swap",
        "upkeep",
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

        self.wait = False

    def parse(self, message:List[str]) -> None:
        if message[1] in self.ACTIONS_TO_IGNORE:
            return
        if message[1] == "gametype":
            self._gametype = message[2]
        if message[1] == "teamsize":
            if message[2] == self._player_role:
                self._player_team_size = int(message[3])
            else:
                self._opponent_team_size = int(message[3])
        else:
            print('unmanaged battle message:', "|".join(message))

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
            active = request.pop('active')
            assert len(active) == 1
            active = active[0]
            if (
                "trapped" in active
                and active.pop("trapped")
            ):
                self.trapped = True
            for i, move in enumerate(active.pop("moves")):
                if "disabled" not in move or not move["disabled"]:
                    self.available_moves.append((i + 1, move))
            if 'canMegaEvo' in active and active.pop('canMegaEvo'):
                self.can_mega_evolve = True
            if 'canZMove' in active:
                self.can_z_move = active.pop('canZMove')
            if 'maybeTrapped' in active:
                active.pop("maybeTrapped")
            if active:
                print('active', active)

        side = request.pop('side')
        if not self.trapped:
            for i, pokemon in enumerate(side["pokemon"]):
                if not pokemon["active"] and pokemon["condition"] != "0 fnt":
                    self.available_switches.append((i + 1, pokemon['ident']))

        for pokemon_info in side['pokemon']:
            self._player_team['ident'] = self._player_team.get(pokemon_info['ident'], Pokemon())
            self._player_team['ident'].update_from_request(pokemon_info)

        request.pop('rqid')
        if 'forceSwitch' in request:
            request.pop('forceSwitch')
        if 'noCancel' in request:
            request.pop('noCancel')
        if 'maybeTrapped' in request:
            request.pop('maybeTrapped')

        if request:
            print('request', request)

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
