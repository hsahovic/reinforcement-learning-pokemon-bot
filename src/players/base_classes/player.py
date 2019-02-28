import asyncio
import json

from abc import ABC, abstractmethod
from random import choice
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
                    await self.select_move(current_battle)

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
                await self.leave_battle(current_battle)
            else:
                current_battle.parse(split_message)

    async def random_move(self, battle: Battle, *, trapped: bool = False) -> None:
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
