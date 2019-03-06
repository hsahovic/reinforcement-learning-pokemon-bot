import asyncio
import json

from players.random_random_battle import RandomRandomBattlePlayer
from players.ml_rk_battle import MLRKBattlePlayer
from environment.utils import CONFIG
from time import time

TARGET_BATTLES = 50
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

    # for player in players:
    #     player.upload_model()
    #     player.fit_from_file("inf581_bot_1")
    #     player.fit_from_file("inf581_bot_2")
    #     player.save_model()
    players[0].upload_model()
    # players[0].fit_from_file("inf581_bot_1")
    # players[0].save_model()

    to_await = []
    for player in players:
        to_await.append(asyncio.ensure_future(player.listen()))
        to_await.append(asyncio.ensure_future(player.run()))

    for el in to_await:
        await el

    print(f"This took {time() - t}s to run.")

n = 1
if __name__ == "__main__":
    for i in range(n):
        print(f"\n{'='*30} STARTING LOOP {i+1} {'='*30}\n")
        asyncio.get_event_loop().run_until_complete(main())
