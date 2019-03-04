from environment.battle import Battle
from environment.utils import data_flattener
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
        state = data_flattener(battle.dic_state)
        assert len(state) == 5390

        # TODO : clean this mess up, when we are kinda sure it works
        # Apparently, we do have six pokemon in each team every time we run, so that
        # is not a problem.

        # Every active pokemon has the right length
        # obj = data_flattener(state['opp_active'])
        # print(len(obj))
        # assert len(obj) == 447
        # obj = data_flattener(state['active'])
        # print(len(obj))
        # if len(obj) != 447:
        #     from pprint import pprint
        #     pprint(state['active'])
        # assert len(obj) == 447

        # # Both team data seem to be working
        # assert len(state['back']) == 5
        # for obj in state['back']:
        #     for move in obj['moves']:
        #         if len(data_flattener(move)) != 98:
        #             from pprint import pprint
        #             print(len(data_flattener(move)))
        #             # pprint(move)
        #     print(len(data_flattener(obj)))
        #     assert len(data_flattener(obj)) == 447
        # obj = data_flattener(state['back'])
        # assert len(obj) == 2235

        # assert len(state['opp_back']) == 5
        # for obj in state['opp_back']:
        #     print(len(data_flattener(obj)))
        #     assert len(data_flattener(obj)) == 447
        # obj = data_flattener(state['opp_back'])
        # assert len(obj) == 2235

        # # Other assertions
        # obj = data_flattener(state['weather'])
        # assert len(obj) == 8
        # obj = data_flattener(state['field'])
        # assert len(obj) == 9
        # obj = data_flattener(state['opp_field'])
        # assert len(obj) == 9
        await self.random_move(battle=battle, trapped=trapped)