from environnement.battle import Battle
from environnement.player import Player

from random import choice


class RandomRandomBattlePlayer(Player):
    def __init__(
        self,
        username: str,
        password: str,
        mode: str = "wait",
        *,
        authentification_address=None,
        avatar: int = None,
        max_concurrent_battles: int = 5,
        server_address: str,
        target_battles: int = 5,
        to_target: str = None,
    ) -> None:
        super(RandomRandomBattlePlayer, self).__init__(
            username=username,
            password=password,
            server_address=server_address,
            mode=mode,
            avatar=avatar,
            authentification_address=authentification_address,
            format="gen7randombattle",
            target_battles=target_battles,
            to_target=to_target,
            max_concurrent_battles=max_concurrent_battles,
        )

    async def select_move(self, battle: Battle, *, trapped: bool = False):
        # TODO : this is dirty and have to be rewritten, i just want to test things out for now
        choices = []
        turn = battle.turn_sent

        if "wait" in battle._player_team and battle._player_team["wait"]:
            return

        if "active" in battle._player_team:
            if (
                "trapped" in battle._player_team["active"][0]
                and battle._player_team["active"][0]["trapped"]
            ):
                trapped = True
            for i, move in enumerate(battle._player_team["active"][0]["moves"]):
                if "disabled" not in move or not move["disabled"]:
                    choices.append(f"/choose move {i + 1}")

        if not trapped:
            for i, pokemon in enumerate(battle._player_team["side"]["pokemon"]):
                if not pokemon["active"] and pokemon["condition"] != "0 fnt":
                    choices.append(f"/choose switch {i + 1}")

        if choices:
            await self.send_message(
                message=choice(choices), message_2=str(turn), room=battle.battle_tag
            )
