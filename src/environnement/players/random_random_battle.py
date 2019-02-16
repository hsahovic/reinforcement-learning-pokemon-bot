from environnement.player import Player


class RandomRandomBattlePlayer(Player):
    def __init__(
        self,
        username: str,
        password: str,
        server_adress: str,
        mode="wait",
        *,
        target_battles=10,
        to_target=None,
    ) -> None:
        super(RandomRandomBattlePlayer, self).__init__(
            username,
            password,
            server_adress,
            mode,
            target_battles=target_battles,
            to_target=to_target,
        )
        self.format = "gen7randombattle"
