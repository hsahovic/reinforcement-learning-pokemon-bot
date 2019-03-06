import asyncio
import json

from players.random_random_battle import RandomRandomBattlePlayer
from players.ml_rk_battle import MLRKBattlePlayer
from environment.utils import CONFIG
from time import time

import numpy as np

TARGET_BATTLES = 20
CONCURRENT_BATTLES = 1


async def main():
    t = time()
    players = [
        MLRKBattlePlayer(
            authentification_address=CONFIG["authentification_address"],
            max_concurrent_battles=CONCURRENT_BATTLES,
            log_messages_in_console=False,
            mode="challenge",
            password=CONFIG["users"][0]["password"],
            server_address=CONFIG["local_adress"],
            target_battles=TARGET_BATTLES,
            to_target=CONFIG["users"][1]["username"],
            username=CONFIG["users"][0]["username"],
        ),
        RandomRandomBattlePlayer(
            authentification_address=CONFIG["authentification_address"],
            log_messages_in_console=False,
            max_concurrent_battles=CONCURRENT_BATTLES,
            mode="wait",
            password=CONFIG["users"][1]["password"],
            server_address=CONFIG["local_adress"],
            target_battles=TARGET_BATTLES,
            username=CONFIG["users"][1]["username"],
        ),
    ]

    players[0].upload_model()

    to_await = []
    for player in players:
        to_await.append(asyncio.ensure_future(player.listen()))
        to_await.append(asyncio.ensure_future(player.run()))

    for el in to_await:
        await el

    print(f"This took {time() - t}s to run.")

if __name__ == "__main__":
    print(f"\n{'='*30} STARTING LOOP {'='*30}\n")
    asyncio.get_event_loop().run_until_complete(main())
