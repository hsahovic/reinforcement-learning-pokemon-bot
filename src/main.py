import asyncio
import websockets

from base_code.io_process import stringing

async def main():
    """
    Loading function. Connect websocket then launch bot.
    """
    async with websockets.connect('ws://sim.smogon.com:8000/showdown/websocket') as websocket:
        while True:
            message = await websocket.recv()
            print("<< {}".format(message))
            await stringing(websocket, message)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    # test()
