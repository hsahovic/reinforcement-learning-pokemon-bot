import asyncio
import json
import websockets

from base_code.io_process import stringing

global CONFIG

CONFIG_PATH = "src/config.json"


async def main(username, password, usage, to_challenge):
    """
    Loading function. Connect websocket then launch bot.
    """
    # Connection on the internet server:
    # async with websockets.connect('ws://sim.smogon.com:8000/showdown/websocket') as websocket:
    
    async with websockets.connect(
        "ws://127.0.0.1:8000/showdown/websocket"
    ) as websocket:
        while True:
            message = await websocket.recv()
            print("<< {}".format(message))
            # Parses messages and launches the bot
            await stringing(
                websocket,
                message,
                usage = usage,
                to_challenge=to_challenge,
                username=username,
                password=password,
            )

async def wrapper():

    username_1 = CONFIG["users"][0]["username"]
    password_1 = CONFIG["users"][0]["password"]

    username_2 = CONFIG["users"][1]["username"]
    password_2 = CONFIG["users"][1]["password"]

    player_1 = asyncio.ensure_future(main(username_1, password_1, 0, username_2))
    player_2 = asyncio.ensure_future(main(username_2, password_2, 1, username_1))

    await player_1
    await player_2

if __name__ == "__main__":
    with open(CONFIG_PATH) as f:
        CONFIG = json.load(f)

    asyncio.get_event_loop().run_until_complete(wrapper())
