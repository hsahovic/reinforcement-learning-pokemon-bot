from environment.battle import Battle
from players.base_classes.player import Player

from pprint import pprint
from random import choice


class MLRandomBattlePlayer(Player):
    def __init__(
        self,
        username: str,
        password: str,
        mode: str = "wait",
        *,
        authentification_address=None,
        avatar: int = None,
        log_messages_in_console: bool = False,
        max_concurrent_battles: int = 5,
        server_address: str,
        target_battles: int = 5,
        to_target: str = None,
    ) -> None:
        super(MLRandomBattlePlayer, self).__init__(
            authentification_address=authentification_address,
            avatar=avatar,
            format="gen7randombattle",
            log_messages_in_console=log_messages_in_console,
            max_concurrent_battles=max_concurrent_battles,
            mode=mode,
            password=password,
            server_address=server_address,
            target_battles=target_battles,
            to_target=to_target,
            username=username,
        )

    async def select_move(self, battle: Battle, *, trapped: bool = False):
        state = battle.dic_state
        print(battle.available_switches)
        print(battle.available_moves)
        print(battle._player_team)
        print(battle._opponent_team)
        print(battle.get_active())
        print(battle.get_opp_active())
        await self.random_move(battle=battle, trapped=trapped)


    async def random_move(self, battle: Battle, *, trapped: bool = False) -> None:
        choices = [f"/choose switch {i}" for i, ident in battle.available_switches] + [
            f"/choose move {i}" for i, move in battle.available_moves
        ]
        turn = battle.turn_sent
        print("################")
        print(choices)

        if choices:
            to_send = choice(choices)
            print(to_send)
            print("#########")
            if "move" in to_send:
                if battle.can_z_move and battle.can_z_move[int(to_send[-1]) - 1]:
                    to_send += " zmove"
                if battle.can_mega_evolve:
                    to_send += " mega"
            await self.send_message(
                message=to_send, message_2=str(turn), room=battle.battle_tag
            )