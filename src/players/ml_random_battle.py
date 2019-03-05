from environment.battle import Battle
from environment.utils import data_flattener
from players.base_classes.player import Player

from pprint import pprint
from random import choices

from keras.models import Sequential
from keras.layers import Dense

import numpy as np


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
        self.model = Sequential()

        self.model.add(Dense(512, input_dim=5390, activation="elu"))
        self.model.add(Dense(128, activation="elu"))
        self.model.add(Dense(20, activation="softmax"))

        self.model.compile(
            loss="categorical_crossentropy", optimizer="rmsprop", metrics=["accuracy"]
        )

        # model.fit(x_train, y_train,
        #           epochs=20,
        #           batch_size=128)
        # score = model.evaluate(x_test, y_test, batch_size=128)

    async def select_move(self, battle: Battle, *, trapped: bool = False):
        state = np.array(data_flattener(battle.dic_state))
        if np.random.rand() < 0.9:
            preds = self.model.predict(np.array([state]))[0]

            moves_probs = preds[:15].reshape((5, 3))
            switch_probs = preds[-5:]
        else:
            moves_probs = np.random.rand(5, 3)
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
            choice = choices(list(range(len(probs))), probs)[0]
            print(self.battles)
            if "data" not in self.battles[battle.battle_tag.split('-')[-1]]:
                self.battles[battle.battle_tag.split('-')[-1]]["data"] = []
            self.battles[battle.battle_tag.split('-')[-1]]["data"].append((state, [int(i == choice) for i in range(len(probs))]))
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
            await self.random_move(battle=battle, trapped=trapped)
