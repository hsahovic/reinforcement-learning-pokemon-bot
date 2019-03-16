import asyncio
import json
import numpy as np

from abc import ABC, abstractmethod
from random import choices
from threading import Thread
from typing import List

from environment.battle import Battle
from players.base_classes.player_network import PlayerNetwork


class Player(PlayerNetwork, ABC):
    def __init__(
        self,
        username: str,
        password: str,
        mode: str,
        *,
        authentification_address: str,
        avatar: int,
        format: str,
        log_messages_in_console: bool,
        max_concurrent_battles: int,
        server_address: str,
        target_battles: int,
        to_target: str,
    ) -> None:
        super(Player, self).__init__(
            authentification_address=authentification_address,
            avatar=avatar,
            log_messages_in_console=log_messages_in_console,
            password=password,
            server_address=server_address,
            username=username,
        )
        self.format = format
        self.max_concurrent_battles = max_concurrent_battles
        self.mode = mode
        self.target_battles = target_battles
        self.to_target = to_target

        self.current_battles = 0
        self.total_battles = 0

        self.battles = {}

        # self._recorded_moves = {"battle_tag": [], "context": [], "decision": []}
        # self._perf = {"nb_battles": [], "accuracy": [], "loss": [], "victories": []}

        self._observations = {}
        self._actions = {}
        self._wins = {}

    async def battle(self, message) -> None:
        messages = message.split("\n")

        split_first_message = messages[0].split("|")
        battle_info = split_first_message[0].split("-")

        for message in messages[1:]:
            split_message = message.split("|")

            # We check that the battle has the correct format
            if battle_info[1] == self.format:
                # Battle initialisation
                if (
                    battle_info[2] not in self.battles
                    and len(split_message) >= 2
                    and split_message[1] == "init"
                ):
                    # TODO: move to add battle ? Overcharge because of team stuff
                    self.battles[battle_info[2]] = Battle(
                        "-".join(battle_info[0:3]), self.username
                    )
                    self.current_battles += 1
                    self.total_battles += 1
                    self._waiting_start = False
                    if "2" in self.username.lower():
                        print(f"Battle %3d / %3d started" % (len(self.battles), self.target_battles))
                # TODO : get opposition team ?
                current_battle = self.battles[battle_info[2]]
            else:
                # TODO
                pass

            if len(split_message) <= 1:
                continue

            # Send move
            if split_message[1] == "request":
                if split_message[2]:
                    current_battle.parse_request(json.loads(split_message[2]))
                if current_battle.is_ready:
                    await self.select_save_move(current_battle)
            elif split_message[1] == "callback" and split_message[2] == "trapped":
                await self.select_save_move(current_battle, trapped=True)

            elif split_message[1] == "error":
                if split_message[2].startswith(
                    "[Invalid choice] There's nothing to choose"
                ):
                    pass
                elif split_message[2].startswith("[Invalid choice] Can't do anything"):
                    pass
                elif split_message[2].startswith("[Invalid choice] Sorry, too late"):
                    pass
                elif split_message[2].startswith("[Invalid choice] Can't switch"):
                    current_battle.trapped = True
                    await self.select_save_move(current_battle)
                elif split_message[2].startswith("[Invalid choice]"):
                    await self.select_save_move(current_battle)

            # Update player id and turn count
            elif (
                split_message[1] == "player"
                and len(split_message) > 3
                and split_message[3] == self.username.lower()
            ):
                if split_message[2] == "p2":
                    current_battle.player_is_p2()
                elif split_message[2] == "p1":
                    current_battle.player_is_p1()

                if current_battle.is_ready:
                    await self.select_save_move(current_battle)

            elif split_message[1] == "win":
                current_battle.won_by(split_message[2])
                # self._observations[current_battle.battle_num].append(current_battle.dic_state)
                # self._actions[current_battle.battle_num].append("/end " + str(int(self.username.lower() == split_message[2])) + "|")
                self._wins[current_battle.battle_num] = int(self.username.lower() == split_message[2])
                self.current_battles -= 1
                # if self.total_battles == self.target_battles:
                #     self.export_perf()
                #     self.export_recorded_moves()

                await self.leave_battle(current_battle)
            elif split_message[1] == "turn":
                if current_battle.is_ready:
                    await self.select_save_move(current_battle)
            else:
                current_battle.parse_message(split_message)

    # def export_perf(self) -> None:
    #     # if len(self._perf["victories"]) == 0:
    #     #     self._perf['victories'].append(np.array([.5]))
    #     self._perf['victories'].append(np.array([self.victory_rate]))
    #     # Prepare export array
    #     export = []
    #     for nb_battles, accuracy, loss, victories in zip(
    #         self._perf["nb_battles"], 
    #         self._perf["accuracy"], 
    #         self._perf["loss"],
    #         self._perf["victories"]):
    #         export.append(np.concatenate((nb_battles, accuracy, loss, victories)))
    #     export = np.array(export, dtype=np.float32)
    #     # Save
    #     with open(self._username + '_perf.csv','ab') as f:
    #         np.savetxt(f, export, delimiter=",", comments="", fmt='%f')

    # def export_recorded_moves(self) -> None:
    #     # Find won battles
    #     won_battle_tags = []
    #     for battle in self.battles.values():
    #         if battle.won:
    #             won_battle_tags.append(int(battle.battle_tag.split('-')[-1]))
    #     # Prepare export array
    #     export = []
    #     for battle_tag, context, decision in zip(
    #         self._recorded_moves["battle_tag"], 
    #         self._recorded_moves["context"], 
    #         self._recorded_moves["decision"]):
    #         if battle_tag in won_battle_tags:
    #             export.append(np.concatenate((battle_tag, context, decision)))
    #     export = np.array(export, dtype=np.int32)
    #     # Save
    #     with open(self._username + '.csv','wb') as f:
    #         np.savetxt(f, export, delimiter=",", comments="", fmt='%i')
    #     # Print message
    #     print(f"PLAYER {self.username}: {self.victory_rate*100:.1f}% of winnings over {self.target_battles} battles")
            

    async def select_save_move(self, battle: Battle, *, trapped: bool = False) -> None:
        if battle.battle_num not in self._observations.keys():
            self._observations[battle.battle_num] = []
            self._actions[battle.battle_num] = []
        self._observations[battle.battle_num].append(battle.dic_state)
        action = await self.select_move(battle, trapped=trapped)
        self._actions[battle.battle_num].append(action)


    async def random_move(self, battle: Battle, *, trapped: bool = False) -> None:
        # The state will be stored, but not directly used.
        state = battle.dic_state

        # Our base ml model generates an array of size 20

        # The 15 first values correspond to move probabilities
        # The 5 last values correspond to switch probabilities to the pokemon in the 
        # back, in the same order as they are given in dic_state and battle.player_back

        # The 15 first values are taken by 3 ; the first 4 group of 3 correspond to (up
        # to) the 4 moves of the active pokemon, as given in the dict state or 
        # battle.active. The last correspond to struggle or recharge.

        # In each group of three, the first value is the probability of using the move,
        # with no megaevolution or zmove
        # The second value refers to using the move as a zmove
        # The third value refers to using the move and mega-evolving

        moves_probs, switch_probs = np.random.rand(5, 3), np.random.rand(5)

        commands = [] # Will contain the equivalent commands

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
            # battle.record_move(state, choice)
            try:
                if commands[choice] == "":
                    raise ValueError('wtf message')
                await self.send_message(
                    message=commands[choice],
                    message_2=str(battle.turn_sent),
                    room=battle.battle_tag,
                )
                return commands[choice]
                
            except (ValueError, IndexError) as e:
                print(e)
                print(probs)
                print(commands)
                print(switch_probs)
                print(moves_probs)
                await self.random_move(battle, trapped=trapped)

    # def record_move(self, battle_tag, context, move: int) -> None:
    #     self._recorded_moves["battle_tag"].append(np.array([battle_tag]))
    #     self._recorded_moves["context"].append(context)
    #     self._recorded_moves["decision"].append(np.array([move]))

    # def record_perf(self, nb_battles, accuracy, loss) -> None:
    #     self._perf["nb_battles"].append(np.array([nb_battles]))
    #     self._perf["accuracy"].append(np.array([accuracy]))
    #     self._perf["loss"].append(np.array([loss]))

    async def run(self) -> None:
        if self.mode == "one_challenge":
            while not self.logged_in:
                asyncio.sleep(0.1)
            await self.challenge()
        elif self.mode == "challenge":
            while self.total_battles < self.target_battles:
                if self.can_accept_challenge:
                    await self.challenge(self.to_target, self.format)
                await asyncio.sleep(0.01)
        elif self.mode == "battle_online":
            # TODO: implement
            pass
        elif self.mode == "wait":
            pass
        else:
            raise ValueError(
                f"Unknown mode {self.mode}. Please specify one of the following modes: 'challenge', 'wait', 'battle_online'"
            )

    @abstractmethod
    def select_move(self, battle: Battle, *, trapped: bool = False) -> str:
        pass

    @property
    def actions(self):
        return self._actions

    @property
    def can_accept_challenge(self) -> bool:
        return (not self._waiting_start) and (
            self.current_battles < self.max_concurrent_battles
            and self.total_battles < self.target_battles
        )

    @property
    def should_die(self) -> bool:
        return (self.total_battles > self.target_battles) or (
            self.total_battles == self.target_battles and self.current_battles == 0
        )

    # @property
    # def moves_data(self):
    #     data = {"context": [], "decision": [], "n_move_in_battle": [], "battle_won": []}
    #     for battle in self.battles.values():
    #         battle_data = battle.moves_data
    #         for context, move in zip(battle_data["context"], battle_data["decision"]):
    #             data["context"].append(context)
    #             data["decision"].append(move)
    #             data["n_move_in_battle"].append(len(battle_data["decision"]))
    #             data["battle_won"].append(battle.won)
    #     return data

    @property
    def observations(self):
        return self._observations

    # @property
    # def victory_rate(self):
    #     victories = 0
    #     total = 0
    #     for battle in self.battles.values():
    #         total += 1
    #         if battle.won:
    #             victories += 1
    #     return victories / total

    @property
    def winning_moves_data(self):
        data = {"observation": [], "action": []}
        for battle_id in self.wins.keys():
            if self.wins[battle_id]:
                for observation, action in zip(self.observations[battle_id], self.actions[battle_id]):
                    data["observation"].append(observation)
                    data["action"].append(action)
        return data
        
    @property
    def wins(self):
        return self._wins

    @property
    def winning_rate(self):
        return sum(self._wins.values())/len(self._wins.values())