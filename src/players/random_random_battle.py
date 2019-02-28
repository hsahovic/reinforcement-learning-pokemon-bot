from environment.battle import Battle
from players.base_classes.player import Player

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
        log_messages_in_console: bool = False,
        max_concurrent_battles: int = 5,
        server_address: str,
        target_battles: int = 5,
        to_target: str = None,
    ) -> None:
        super(RandomRandomBattlePlayer, self).__init__(
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
        choices = [f"/choose switch {i}" for i, ident in battle.available_switches] + [
            f"/choose move {i}" for i, move in battle.available_moves
        ]
        turn = battle.turn_sent

        if choices:
            to_send = choice(choices)
            if "move" in to_send:
                if battle.can_z_move and battle.can_z_move[int(to_send[-1]) - 1]:
                    to_send += " zmove"
                if battle.can_mega_evolve:
                    to_send += " mega"
            await self.send_message(
                message=to_send, message_2=str(turn), room=battle.battle_tag
            )
