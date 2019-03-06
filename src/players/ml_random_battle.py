from environment.battle import Battle
from environment.utils import CONFIG, data_flattener
from players.base_classes.player import Player
from players.random_random_battle import RandomRandomBattlePlayer

from pprint import pprint
from random import choices

from keras.models import load_model, Sequential
from keras.layers import Dense

import asyncio
import numpy as np
import os
import time


# TODO
# Save json data and models
# Perfs


class ModelManager:

    MODEL_DIRECTORY = "models/h/"

    def __init__(self):
        self.model = Sequential()

        self.model.add(Dense(512, input_dim=5390, activation="elu"))
        # self.model.add(Dense(128, activation="elu"))
        self.model.add(Dense(20, activation="softmax"))

        self.model.compile(
            loss="categorical_crossentropy", optimizer="rmsprop", metrics=["accuracy"]
        )

        print(self.model.summary())

    def feed(self, x):
        x = self.format_x(x)
        preds = self.model.predict(np.array([x]))[0]
        return preds[:15].reshape((5, 3)), preds[-5:]

    def format_x(self, state):
        return data_flattener(state)

    async def initial_training(
        self, number_of_battles=1000, concurrent_battles=100, log_messages=False
    ):
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

        x = (
            players[0].winning_moves_data["context"]
            + players[1].winning_moves_data["context"]
        )
        y = (
            players[0].winning_moves_data["decision"]
            + players[1].winning_moves_data["decision"]
        )

        self.train(x, y)

    def load(self, name=None):
        """
        Loads a model.

        If a name is given, it will be fetched in the models directory.
        Otherwise, the last model will be loaded.
        """
        if name:
            self.model = load_model(self.MODEL_DIRECTORY + name)
        else:
            models = os.listdir(self.MODEL_DIRECTORY)
            if models:
                self.load(sorted(models)[-1])
            else:
                raise ValueError("No models to load were found.")

    def train(self, x, y):
        x = np.array([self.format_x(el) for el in x])
        y_t = np.zeros(shape=(len(y), 20))
        for i, val in enumerate(y):
            y_t[i, val] = 1
        self.model.fit(x, y_t, epochs=3, batch_size=64)
        self.model.save(self.MODEL_DIRECTORY + f"{time.time()}.model")

    async def self_training(
        self,
        iterations=5,
        number_of_battles=100,
        concurrent_battles=100,
        log_messages=False,
    ):
        for i in range(iterations):
            players = [
                MLRandomBattlePlayer(
                    authentification_address=CONFIG["authentification_address"],
                    max_concurrent_battles=concurrent_battles,
                    log_messages_in_console=log_messages,
                    mode="challenge",
                    model_manager=self,
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

            print(f"Round {i + 1} finished.")

            x = (
                players[0].winning_moves_data["context"]
                + players[1].winning_moves_data["context"]
            )
            y = (
                players[0].winning_moves_data["decision"]
                + players[1].winning_moves_data["decision"]
            )

            self.train(x, y)


class MLRandomBattlePlayer(Player):
    def __init__(
        self,
        username: str,
        password: str,
        mode: str,
        model_manager: ModelManager,
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
        # The state will be stored, but not directly used.
        state = battle.dic_state

        # Our base ml model generates an array of size 20

        # The 15 first values correspond to move probabilities
        # The 5 last values correspond to switch probabilities to the pokemon in the
        # back, in the same order as they are given in dic_state and battle.player_back

        # The 15 first values are taken by 3 ; the first 4 group of 3 correspond to (up
        # to) the 4 moves of the active pokemon, as given in the dict state or
        # battle.active. The last correspond to Struggle.

        # In each group of three, the first value is the probability of using the move,
        # with no megaevolution or zmove
        # The second value refers to using the move as a zmove
        # The third value refers to using the move and mega-evolving

        if np.random.rand() < 0.9:
            moves_probs, switch_probs = self.model_manager.feed(state)
        else:
            moves_probs, switch_probs = np.random.rand(5, 3), np.random.rand(5)

        commands = []  # Will contain the equivalent commands

        # Pokemon species as key, order id as value
        available_switches = {
            battle._player_team[el[1][4:]].species: el[0]
            for el in battle.available_switches
        }

        # Move name as key, order id as value
        available_moves = {
            el[1]["id"]: el[0] for el in battle.available_moves if "id" in el[1]
        }

        # Move names
        available_z_moves = []

        # TODO : check
        if battle.can_z_move:
            for move, can_z in zip(battle.active_moves, battle.can_z_move):
                if can_z:
                    available_z_moves.append(move)

        # Setting pokemon switches information
        for i, pokemon in enumerate(battle.player_back):
            if pokemon not in available_switches:
                commands.append("")
                switch_probs[i] = 0
            else:
                commands.append(f"/switch {available_switches[pokemon]}")

        if trapped:
            switch_probs[:] = 0

        # TODO : check
        for i in range(len(battle.player_back), 5):
            commands.append("")
            switch_probs[i] = 0

        # Setting attacks information
        for j, move in enumerate(battle.active_moves):
            if move not in available_moves:
                commands.append("")
                commands.append("")
                commands.append("")
                moves_probs[j, :] = 0
            else:
                if move not in available_z_moves:
                    moves_probs[j, 1] = 0
                if not battle.can_mega_evolve:
                    moves_probs[j, 2] = 0
                commands.append(f"/choose move {available_moves[move]}")
                commands.append(f"/choose move {available_moves[move]} zmove")
                commands.append(f"/choose move {available_moves[move]} mega")

        for i in range(len(battle.active_moves), 4):
            moves_probs[i, :] = 0
            commands.append("")
            commands.append("")
            commands.append("")

        if "struggle" in available_moves:
            commands.append(f"/choose move struggle")
        elif "recharge" in available_moves:
            commands.append(f"/choose move recharge")
        else:
            moves_probs[4, 0] = 0
        commands.append("")
        commands.append("")
        moves_probs[4, 1:] = 0

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
            choice = choices([i for i, val in enumerate(probs)], probs)[0]
            battle.record_move(state, choice)
            try:
                if commands[choice] == "":
                    raise ValueError("wtf message")
                await self.send_message(
                    message=commands[choice],
                    message_2=str(battle.turn_sent),
                    room=battle.battle_tag,
                )
                return
            except (ValueError, IndexError) as e:
                await self.random_move(battle, trapped=trapped)
        else:
            await self.random_move(battle, trapped=trapped)

        # print(available_switches)
        # print(battle.player_back)
        # print(available_moves)
        # print(battle.active_moves)
        # print(probs)
        # print(commands)
        # print(switch_probs)
        # print(moves_probs)