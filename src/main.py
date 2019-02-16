import asyncio
import json

from environnement.players.random_random_battle import RandomRandomBattlePlayer

global CONFIG

CONFIG_PATH = "src/config.json"


async def main():
    players = [
        RandomRandomBattlePlayer(
            CONFIG["users"][0]["username"],
            CONFIG["users"][0]["password"],
            CONFIG["local_adress"],
            mode="challenge",
            to_target=CONFIG["users"][1]["username"],
        ),
        RandomRandomBattlePlayer(
            CONFIG["users"][1]["username"],
            CONFIG["users"][1]["password"],
            CONFIG["local_adress"],
            mode="wait",
        ),
    ]

    to_await = []
    for player in players:
        to_await.append(asyncio.ensure_future(player.listen()))
        to_await.append(asyncio.ensure_future(player.run()))

    for el in to_await:
        await el


if __name__ == "__main__":
    with open(CONFIG_PATH) as f:
        CONFIG = json.load(f)
    asyncio.get_event_loop().run_until_complete(main())
