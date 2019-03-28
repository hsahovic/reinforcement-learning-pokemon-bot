# -*- coding: utf-8 -*-
"""
ML Model Manager abstract class and corresponding private ML Random Battle Player.

This file is part of the pokemon showdown reinforcement learning bot project,
created by Randy Kotti, Ombeline Lagé and Haris Sahovic as part of their
advanced topics in artifical intelligence course at Ecole Polytechnique.
"""

from environment.battle import Battle
from environment.utils import CONFIG
from players.base_classes.player import Player
from players.random_random_battle import RandomRandomBattlePlayer

from abc import ABC, abstractmethod
from random import choices
from typing import Tuple

import tensorflow as tf

import asyncio
import numpy as np
import os
import time

import matplotlib.pyplot as plt
plt.style.use("ggplot")

class ModelManagerTF(ABC):

    MODEL_NAME = None

    def __init__(self) -> None:
        """
        This method should be rewritten when inherited.

        You need to define and compile a TF model.
        """
        self.sess = None
        pass

    def feed(self, x: dict) -> Tuple[np.array, np.array]:
        """
        Return move probabilities from battle state

        Args:
            x (dict): battle state to be transformed

        Returns:
            moves_predictions (np.array(5,3)), switch_predictions(np.array(5))
        """
        x = self.format_x(x)
        preds = self.predict(np.array([x]))[0]
        return preds[:15].reshape((5, 3)), preds[-5:]

    @abstractmethod
    def format_x(self, state: dict):
        """
        Formats battle_state into usable input for the model.
        You should rewrite this method when inherited.

        Args:
            state (dict): battle state

        Returns:
            x: model input
        """
        pass

    async def initial_training(
        self, number_of_battles=100, concurrent_battles=10, log_messages=False
    ) -> None:
        """
        Initiate model with training data gathered from random battles.

        Args:
            number_of_battles (int, defaults to 100): number of battles to run

            concurrent_battles (int, defaults to 10): number of battles to be run 
            concurrently

            log_messages (bool, defaults to False): wheter to log battles messages
        """
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
        
        for player in players:
            self.train(
                player.observations,
                player.actions,
                player.wins
            )

        del players

    def close(self) -> None:
        """
        Closes TF session
        """
        self.sess.close()

    def load(self, name=None) -> None:
        """
        Loads a model.

        If a name is given, it will be fetched in the models directory.
        Otherwise, the last model will be loaded.

        Args:
            name (str, defaults to None): name of the model to be loaded. If None, the 
            last saved model will be used.
        """
        if self.MODEL_NAME is None:
            raise ValueError(
                """self.MODEL_NAME is None. Are you sure you initialised your 
            model with a name attribute ?
        """
            )
        if not os.path.isdir(os.path.join("models", self.MODEL_NAME)):
            raise ValueError("No models to load were found.")
        
        if name:
            tf.train.Saver().restore(self.sess, os.path.join("models", self.MODEL_NAME, name))
        else:
            models = os.listdir(os.path.join("models", self.MODEL_NAME))
            if models:
                tf.train.Saver().restore(self.sess, tf.train.latest_checkpoint(os.path.join("models", self.MODEL_NAME)))
            else:
                raise ValueError("No models to load were found.")

    def get_player(
        self,
        username: str,
        password: str,
        mode: str,
        *,
        authentification_address=None,
        avatar: int = None,
        epsilon: float = 0.9,
        log_messages_in_console: bool = False,
        max_concurrent_battles: int = 5,
        server_address: str,
        target_battles: int = 5,
        to_target: str = None,
    ) -> Player:
        """
        Creates an MLRandomBattlePlayer with specified parameters.
        """
        return _MLRandomBattlePlayer(
            username,
            password,
            mode,
            self,
            authentification_address=authentification_address,
            avatar=avatar,
            epsilon=epsilon,
            log_messages_in_console=log_messages_in_console,
            max_concurrent_battles=max_concurrent_battles,
            server_address=server_address,
            target_battles=target_battles,
            to_target=to_target,
        )

    def save(self, name=None) -> None:
        """ 
        Save current model
        """
        if name == None:
            name = str(int(time.time()))
        if not os.path.isdir(os.path.join("models", self.MODEL_NAME)):
            os.makedirs(os.path.join("models", self.MODEL_NAME))
        tf.train.Saver().save(self.sess, os.path.join("models", self.MODEL_NAME, name))

    @abstractmethod
    def predict(self, x):
        """
        Predicts action probabilities given environment features x
        You should rewrite this method when inherited.

        Args:
            x : already transformed features

        Returns:
            y : array of probabilities for actions
        """
        pass

    @abstractmethod
    def train(self, observations, actions, wins) -> None:
        """
        Trains the model on observations, actions, wins.

        Args:
            observations: raw input data to be used with self.format

            actions: move choices, as str
        """
        pass

    async def test(
        self,
        number_of_battles=50,
        concurrent_battles=5,
        log_messages=False,
        opponent = "random"
    ):
        """
        Tests the model against opponent

        Args:
            number_of_battles (int, defaults to 100): number of battles to run

            concurrent_battles (int, defaults to 10): number of battles to be run 
            concurrently

            log_messages (bool, defaults to True): wheter to log battles messages

            opponent (str, defaults to random): opposing agent
        """
        players = [
            self.get_player(
                authentification_address=CONFIG["authentification_address"],
                epsilon=0.95,
                max_concurrent_battles=concurrent_battles,
                log_messages_in_console=log_messages,
                mode="challenge",
                password=CONFIG["users"][0]["password"],
                server_address=CONFIG["local_adress"],
                target_battles=number_of_battles,
                to_target=CONFIG["users"][1]["username"],
                username=CONFIG["users"][0]["username"],
            )]

        if opponent == "random":
            players.append(
                RandomRandomBattlePlayer(
                    authentification_address=CONFIG["authentification_address"],
                    log_messages_in_console=log_messages,
                    max_concurrent_battles=concurrent_battles,
                    mode="wait",
                    password=CONFIG["users"][1]["password"],
                    server_address=CONFIG["local_adress"],
                    target_battles=number_of_battles,
                    username=CONFIG["users"][1]["username"],
                ))

        to_await = []
        for player in players:
            to_await.append(asyncio.ensure_future(player.listen()))
            to_await.append(asyncio.ensure_future(player.run()))

        for el in to_await:
            await el

        winning_rate = players[0].winning_rate

        del players

        return winning_rate
    
    async def self_training(
        self,
        iterations=5,
        number_of_battles=100,
        concurrent_battles=10,
        testing_step=1,
        log_messages=True,
        display=True
    ):
        """
        Trains the model with data gathered from self vs. self battles.

        Args:
            number_of_battles (int, defaults to 100): number of battles to run

            concurrent_battles (int, defaults to 10): number of battles to be run 
            concurrently

            log_messages (bool, defaults to True): wheter to log battles messages
        """
        perf_record = []
        print(f"\n{'='*10} STARTING LOOP {'='*10}\n")
        print(f"{'-'*10} Testing {'-'*10}")
        perf = await self.test(number_of_battles=20)
        perf_record.append(perf)
        print(f"\n{'*'*15} Performance: {perf*100:2.1f}% {'*'*15}\n")
        for i in range(iterations):
            print(f"\n{'='*10} STARTING ITERATION {i+1} {'='*10}\n")
            players = [
                self.get_player(
                    authentification_address=CONFIG["authentification_address"],
                    epsilon=0.95,
                    max_concurrent_battles=concurrent_battles,
                    log_messages_in_console=log_messages,
                    mode="challenge",
                    password=CONFIG["users"][0]["password"],
                    server_address=CONFIG["local_adress"],
                    target_battles=number_of_battles,
                    to_target=CONFIG["users"][1]["username"],
                    username=CONFIG["users"][0]["username"],
                ),
                self.get_player(
                    authentification_address=CONFIG["authentification_address"],
                    epsilon=0.95,
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

            print(f"{'-'*10} Fighting {'-'*10}")
            for el in to_await:
                await el

            print(f"{'-'*10} Training {'-'*10}")
            for player in players:
                self.train(
                    player.observations,
                    player.actions,
                    player.wins
                )
            if (i+1)%testing_step == 0:
                print(f"{'-'*10} Testing {'-'*10}")
                perf = await self.test(number_of_battles=20)
                perf_record.append(perf)
                print(f"\n{'*'*15} Performance: {perf*100:2.1f}% {'*'*15}\n")
            
            del players
        
        if display:
            window = 5
            sliding_perf = [np.average(perf_record[max(0,i-window):i+1]) for i in range(len(perf_record))]
            plt.plot(np.array(range(len(perf_record)))*testing_step, sliding_perf, color='blue')
            plt.plot(np.array(range(len(perf_record)))*testing_step, [0.5]*len(perf_record), color='red', ls='--')
            plt.xlim([0, iterations])
            plt.ylim([0,1])
            plt.xlabel("Number of iterations")
            plt.ylabel("Performance")
            plt.savefig("perf.png")
            plt.show()
        
        self.close()


class _MLRandomBattlePlayer(Player):
    def __init__(
        self,
        username: str,
        password: str,
        mode: str,
        model_manager: ModelManagerTF,
        *,
        authentification_address=None,
        avatar: int = None,
        epsilon: float = 0.9,
        log_messages_in_console: bool = False,
        max_concurrent_battles: int = 5,
        server_address: str,
        target_battles: int = 5,
        to_target: str = None,
    ) -> None:
        super(_MLRandomBattlePlayer, self).__init__(
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
        self.epsilon = epsilon
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

        if np.random.rand() < self.epsilon:
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
            try:
                if commands[choice] == "":
                    raise ValueError("wtf message")
                await self.send_message(
                    message=commands[choice],
                    message_2=str(battle.turn_sent),
                    room=battle.battle_tag,
                )
                return choice
            except (ValueError, IndexError) as e:
                await self.random_move(battle, trapped=trapped)
        else:
            await self.random_move(battle, trapped=trapped)
