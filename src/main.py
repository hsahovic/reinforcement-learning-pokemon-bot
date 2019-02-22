import asyncio
import json

from environnement.players.random_random_battle import RandomRandomBattlePlayer

global CONFIG

CONFIG_PATH = "src/config.json"
TARGET_BATTLES = 10

async def main():
    # TODO : investigate concurrency
    players = [
        RandomRandomBattlePlayer(
            authentification_address=CONFIG["authentification_address"],
            max_concurrent_battles=1,
            mode="challenge",
            password=CONFIG["users"][0]["password"],
            server_address=CONFIG["local_adress"],
            target_battles=TARGET_BATTLES,
            to_target=CONFIG["users"][1]["username"],
            username=CONFIG["users"][0]["username"],
        ),
        RandomRandomBattlePlayer(
            authentification_address=CONFIG["authentification_address"],
            mode="wait",
            password=CONFIG["users"][1]["password"],
            server_address=CONFIG["local_adress"],
            target_battles=TARGET_BATTLES,
            username=CONFIG["users"][1]["username"],
        ),
    ]

    to_await = []
    for player in players:
        to_await.append(asyncio.ensure_future(player.listen()))
        to_await.append(asyncio.ensure_future(player.run()))

    for el in to_await:
        await el


if __name__ == "__main__":
    print(f"\n{'='*30} STARTING {'='*30}\n")
    with open(CONFIG_PATH) as f:
        CONFIG = json.load(f)
    asyncio.get_event_loop().run_until_complete(main())
