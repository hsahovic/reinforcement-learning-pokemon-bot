class Battle:
    def __init__(self, battle_tag: str, player_name: str) -> None:
        while battle_tag.endswith("\n"):
            battle_tag = battle_tag[:-1]
        self._player_team = {}
        self._opponent_team = {}
        if battle_tag.startswith(">"):
            battle_tag = battle_tag[1:]
        self._battle_tag = battle_tag
        self._turn = 0
        self._player_role = None
        self._finished = False
        self._winner = None
        self._won = None
        self._player_name = player_name

    def update_team(self, team: dict) -> None:
        # TODO : pokemon stuff hehehe
        self._player_team = team
        self._turn += 1

    def player_is_p1(self) -> None:
        self._player_role = 0

    def player_is_p2(self) -> None:
        self._player_role = 1

    def set_turn(self, turn: int) -> None:
        return
        # self._turn = turn

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
        return self._turn * 2 + self._player_role
