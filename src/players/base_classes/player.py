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

        self._recorded_moves = {"battle_tag": [], "context": [], "decision": []}

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
                    current_battle.update_from_request(json.loads(split_message[2]))
                if current_battle.is_ready:
                    # print('yiiiihi')
                    await self.select_move(current_battle)
                # else:
                # print("ooooh :'(")
            elif split_message[1] == "callback" and split_message[2] == "trapped":
                await self.select_move(current_battle, trapped=True)

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
                    await self.select_move(current_battle)
                elif split_message[2].startswith("[Invalid choice]"):
                    await self.select_move(current_battle)

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
                    await self.select_move(current_battle)

            elif split_message[1] == "win":
                current_battle.won_by(split_message[2])
                self.current_battles -= 1
                print(self.total_battles)
                if self.total_battles == self.target_battles:
                    self.export_recorded_moves()

                await self.leave_battle(current_battle)
            elif split_message[1] == "turn":
                if current_battle.is_ready:
                    await self.select_move(current_battle)
            else:
                current_battle.parse(split_message)

    def export_recorded_moves(self) -> None:
        won_battle_tags = []
        for battle in self.battles.values():
            if battle.won:
                won_battle_tags.append(int(battle.battle_tag.split('-')[-1]))
        export = []
        for battle_tag, context, decision in zip(
            self._recorded_moves["battle_tag"], 
            self._recorded_moves["context"], 
            self._recorded_moves["decision"]):
            if battle_tag in won_battle_tags:
                export.append(np.concatenate((battle_tag, context, decision)))
        export = np.array(export, dtype=np.int32)
        np.savetxt(self._username + ".csv", export, 
            delimiter=",", comments="", fmt='%i')
        print(f"PLAYER {self.username}: {len(won_battle_tags)*100/self.target_battles:.1f}% of winnings over {self.target_battles} battles")
            
    async def random_move(self, battle: Battle, *, trapped: bool = False) -> None:
        # This is a base for further work, especially concerning data output in ML
        moves_probs = np.random.rand(5, 3)
        # 5th for struggle ; 2 and 3 for zmove / mega
        switch_probs = np.random.rand(5)

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
                moves_probs[i, 0] = 0
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
        else:
            print(moves_probs)
        moves_probs[4, 1:] = 0

        if not battle.can_mega_evolve:
            moves_probs[:, 2] = 0

        else:
            moves_probs[:, 1] = 0

        probs = []
        for i, p in enumerate(switch_probs):
            probs.append(p)

        for i, prob in enumerate(moves_probs):
            p, z, m = prob
            probs.append(p * (1 - z) * (1 - m))
            probs.append(p * z)
            probs.append(p * m)

        probs = np.array(probs)
        if sum(probs):
            probs /= sum(probs)
            try:
                await self.send_message(
                    message=choices(commands, probs)[0],
                    message_2=str(battle.turn_sent),
                    room=battle.battle_tag,
                )
            except ValueError:
                print(probs)
                print(commands)
                print(switch_probs)
                print(moves_probs)

    def record_move(self, battle_tag, context, move: int) -> None:
        self._recorded_moves["battle_tag"].append(np.array([battle_tag]))
        self._recorded_moves["context"].append(context)
        self._recorded_moves["decision"].append(np.array([move]))

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
    def select_move(self, battle: Battle, *, trapped: bool = False) -> None:
        pass

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

    @property
    def moves_data(self):
        data = {"context": [], "move": [], "n_move_in_battle": [], "battle_won": []}
        for battle in self.battles.values():
            data = battle.moves_data
            for context, move in zip(data["context"], data["move"]):
                data["context"].append(context)
                data["move"].append(move)
                data["n_move_in_battle"].append(len(data["move"]))
                data["battle_won"].append(battle.won)

    @property
    def winning_moves_data(self):
        data = {"context": [], "move": [], "n_move_in_battle": []}
        for battle in self.battles.values():
            if not battle.won:
                continue
            data = battle.moves_data
            for context, move in zip(data["context"], data["move"]):
                data["context"].append(context)
                data["move"].append(move)
                data["n_move_in_battle"].append(len(data["move"]))

