import asyncio
import json

from threading import Thread
from typing import List

from environnement.battle import Battle
from environnement.player_network import PlayerNetwork

from abc import ABC, abstractmethod


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
        max_concurrent_battles: int,
        server_address: str,
        target_battles: int,
        to_target: str,
    ) -> None:
        super(Player, self).__init__(
            username=username,
            password=password,
            server_address=server_address,
            authentification_address=authentification_address,
            avatar=avatar,
        )
        self.format = format
        self.mode = mode
        self.target_battles = target_battles
        self.max_concurrent_battles = max_concurrent_battles
        self.to_target = to_target

        self.current_battles = 0
        self.total_battles = 0

        self.battles = {}

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
                # TODO : get opposition team ?
                elif battle_info[2] in self.battles:
                    current_battle = self.battles[battle_info[2]]

                else:
                    # TODO
                    pass
            else:
                # TODO
                pass

            if len(split_message) <= 1:
                continue

            if split_message[-2] == "turn":
                current_battle.set_turn(int(split_message[-1]))

            # Send move
            if split_message[1] == "request":
                if split_message[2]:
                    current_battle.update_team(json.loads(split_message[2]))
                if current_battle.is_ready:
                    await self.select_move(current_battle)

            elif split_message[1] == "callback" and split_message[2] == "trapped":
                await self.select_move(current_battle, trapped=True)

            elif split_message[1] == "error":
                if split_message[2].startswith("[Invalid choice]"):
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
                self.leave_battle(current_battle)
            else:
                pass

    async def run(self) -> None:
        if self.mode == "one_challenge":
            asyncio.sleep(5)
            await self.challenge()
        elif self.mode == "challenge":
            while self.total_battles < self.target_battles:
                if self.can_accept_challenge:
                    await self.challenge(self.to_target, self.format)
                await asyncio.sleep(0.1)
        elif self.mode == "battle_online":
            # TODO: implement
            pass
        elif self.mode == "wait":
            pass
        else:
            raise ValueError(
                f"Unknown mode {self.mode}. Please specify one of the following modes: 'challenge', 'wait', 'battle_online'"
            )

    @property
    def can_accept_challenge(self) -> bool:
        return (
            self.current_battles < self.max_concurrent_battles
            and self.total_battles < self.target_battles
        )

    @property
    def should_die(self) -> bool:
        return (self.total_battles > self.target_battles) or (
            self.total_battles == self.target_battles and self.current_battles == 0
        )

    @abstractmethod
    def select_move(self, battle: Battle, *, trapped: bool = False) -> None:
        pass
