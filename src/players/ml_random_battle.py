from environment.battle import Battle
from environment.utils import CONFIG, data_flattener
from players.base_classes.player import Player
from players.random_random_battle import RandomRandomBattlePlayer

from pprint import pprint
from random import choices

from keras.models import Sequential
from keras.layers import Dense

import asyncio
import numpy as np


class ModelManager:

    def __init__(self):
        self.model = Sequential()

        self.model.add(Dense(512, input_dim=5390, activation="elu"))
        self.model.add(Dense(128, activation="elu"))
        self.model.add(Dense(20, activation="softmax"))

        self.model.compile(
            loss="categorical_crossentropy", optimizer="rmsprop", metrics=["accuracy"]
        )

        print(self.model.summary())

    def feed(self, state):
        x = self.format_x(state)
        preds = self.model.predict(np.array([x]))[0]
        return preds[:15].reshape((5, 3)), preds[-5:]

    def format_x(self, state):
        return data_flattener(state)

    async def initial_training(self, number_of_battles=10, concurrent_battles = 10, log_messages=True):
        players = [
            RandomRandomBattlePlayer(
                authentification_address=CONFIG["authentification_address"],
                max_concurrent_battles=concurrent_battles,
                log_messages_in_console=log_messages,
                mode="challenge",
                password=CONFIG["users"][0]["password"],
                server_address=CONFIG["local_adress"],
                target_battles=number_of_battles,
                to_target=CONFIG["users"][1]["username"],
                username=CONFIG["users"][0]["username"],
            ),
            RandomRandomBattlePlayer(
                authentification_address=CONFIG["authentification_address"],
                log_messages_in_console=log_messages,
                max_concurrent_battles=concurrent_battles,
                mode="wait",
                password=CONFIG["users"][1]["password"],
                server_address=CONFIG["local_adress"],
                target_battles=number_of_battles,
                username=CONFIG["users"][1]["username"],
            ),
        ]
        to_await = []
        for player in players:
            to_await.append(asyncio.ensure_future(player.listen()))
            to_await.append(asyncio.ensure_future(player.run()))

        for el in to_await:
            await el

        print("Initial battles finished.")

        x = players[0].winning_moves_data['context'] + players[1].winning_moves_data['context']
        y = players[0].winning_moves_data['decision'] + players[1].winning_moves_data['decision']

        self.train(x, y)

    def train(self, x, y):
        x = np.array([self.format_x(el) for el in x])
        y_t = np.zeros(shape = (len(y), 20))
        for i, val in enumerate(y):
            y_t[i, val] = 1
        self.model.fit(x, y_t, epochs = 3, batch_size = 64)

    async def self_training(self, iterations = 5, number_of_battles=10, concurrent_battles = 10, log_messages=True):
        for _ in range(iterations):
            players = [
                MLRandomBattlePlayer(
                    authentification_address=CONFIG["authentification_address"],
                    max_concurrent_battles=concurrent_battles,
                    log_messages_in_console=log_messages,
                    mode="challenge",
                    model_manager = self,
                    password=CONFIG["users"][0]["password"],
                    server_address=CONFIG["local_adress"],
                    target_battles=number_of_battles,
                    to_target=CONFIG["users"][1]["username"],
                    username=CONFIG["users"][0]["username"],
                ),
                MLRandomBattlePlayer(
                    authentification_address=CONFIG["authentification_address"],
                    log_messages_in_console=log_messages,
                    max_concurrent_battles=concurrent_battles,
                    mode="wait",
                    model_manager=self,
                    password=CONFIG["users"][1]["password"],
                    server_address=CONFIG["local_adress"],
                    target_battles=number_of_battles,
                    username=CONFIG["users"][1]["username"],
                ),
            ]
            to_await = []
            for player in players:
                to_await.append(asyncio.ensure_future(player.listen()))
                to_await.append(asyncio.ensure_future(player.run()))

            for el in to_await:
                await el

            print("One round finished.")

            x = players[0].winning_moves_data['context'] + players[1].winning_moves_data['context']
            y = players[0].winning_moves_data['decision'] + players[1].winning_moves_data['decision']

            self.train(x, y)

class MLRandomBattlePlayer(Player):
    def __init__(
        self,
        username: str,
        password: str,
        mode: str,
        model_manager:ModelManager,
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
        self.model_manager = model_manager

    async def select_move(self, battle: Battle, *, trapped: bool = False):
        state = battle.dic_state
        if np.random.rand() < 0.9:
            moves_probs, switch_probs = self.model_manager.feed(state)
        else:
            moves_probs, switch_probs = np.random.rand(5, 3), np.random.rand(5)

        commands = []

        available_switches = {
            battle._player_team[el[1][4:]].species: el[0]
            for el in battle.available_switches
        }
        for i, pokemon in enumerate(battle.player_back):
            if pokemon not in available_switches:
                commands.append("")
                switch_probs[i] = 0
            else:
                commands.append(f"/switch {available_switches[pokemon]}")
        switch_probs[i + 1 :] = 0

        available_moves = {
            el[1]["id"]: el[0] for el in battle.available_moves if "id" in el[1]
        }
        for i, move in enumerate(battle.active_moves):
            if move not in available_moves:
                commands.append("")
                commands.append("")
                commands.append("")
                moves_probs[i, :] = 0
            else:
                if not (
                    battle.can_z_move
                    and available_moves[move] in battle.can_z_move
                    and battle.can_z_move[available_moves[move]]
                ):
                    moves_probs[i, 1] = 0
                commands.append(f"/choose move {available_moves[move]}")
                commands.append(f"/choose move {available_moves[move]} zmove")
                commands.append(f"/choose move {available_moves[move]} mega")

        for i in range(i, 3):
            moves_probs[i, 0] = 0
            commands.append(f"")
            commands.append(f"")
            commands.append(f"")
        commands.append(f"/choose move struggle")
        commands.append(f"")
        commands.append(f"")
        if "struggle" not in available_moves:
            moves_probs[4, 0] = 0
        moves_probs[4, 1:] = 0

        if not battle.can_mega_evolve:
            moves_probs[:, 2] = 0

        else:
            moves_probs[:, 1] = 0

        if trapped:
            switch_probs[:] = 0

        probs = []
        for i, p in enumerate(switch_probs):
            probs.append(p)

        for i, prob in enumerate(moves_probs):
            p, z, m = prob
            probs.append(p)
            probs.append(z)
            probs.append(m)

        probs = np.array(probs)
        if sum(probs):
            probs /= sum(probs)
            choice = choices(list(range(len(probs))), probs)[0]
            battle.record_move(state, choice)
            try:
                await self.send_message(
                    message=commands[choice],
                    message_2=str(battle.turn_sent),
                    room=battle.battle_tag,
                )
                return
            except ValueError:
                print(probs)
                print(commands)
                print(switch_probs)
                print(moves_probs)
        if available_moves or available_switches:
            print('An error occured ?')
            await self.random_move(battle=battle, trapped=trapped)
