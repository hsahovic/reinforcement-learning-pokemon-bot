import asyncio
import json

from players.random_random_battle import RandomRandomBattlePlayer
from players.ml_rk_battle import MLRKBattlePlayer
from environment.utils import CONFIG
from time import time

import numpy as np
import matplotlib.pyplot as plt

TARGET_BATTLES = 5
CONCURRENT_BATTLES = 1


async def main():
    t = time()
    players = [
        MLRKBattlePlayer(
            authentification_address=CONFIG["authentification_address"],
            max_concurrent_battles=CONCURRENT_BATTLES,
            log_messages_in_console=True,
            mode="challenge",
            password=CONFIG["users"][0]["password"],
            server_address=CONFIG["local_adress"],
            target_battles=TARGET_BATTLES,
            to_target=CONFIG["users"][1]["username"],
            username=CONFIG["users"][0]["username"],
        ),
        RandomRandomBattlePlayer(
            authentification_address=CONFIG["authentification_address"],
            log_messages_in_console=True,
            max_concurrent_battles=CONCURRENT_BATTLES,
            mode="wait",
            password=CONFIG["users"][1]["password"],
            server_address=CONFIG["local_adress"],
            target_battles=TARGET_BATTLES,
            username=CONFIG["users"][1]["username"],
        ),
    ]

    init = False
    train = (TARGET_BATTLES == 5)

    if init:
        players[0].reset_weights()
        players[0].save_model()
    players[0].upload_model()

    if train:
        players[0].fit_from_file("inf581_bot_1")

    to_await = []
    for player in players:
        to_await.append(asyncio.ensure_future(player.listen()))
        to_await.append(asyncio.ensure_future(player.run()))

    for el in to_await:
        await el

    print(f"This took {time() - t}s to run.")
    
    players[0].save_model() 
    if not train:
        with open('perf.csv','ab') as f:
            np.savetxt(f, np.array([players[0].nb_battles, players[0].victory_rate]).reshape(1,-1), delimiter=",", comments="", fmt='%f')

n = 0
if __name__ == "__main__":
    for i in range(n):
        print(f"\n{'='*30} STARTING LOOP {i+1} {'='*30}\n")
        asyncio.get_event_loop().run_until_complete(main())
